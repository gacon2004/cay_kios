from __future__ import annotations
import pymysql
from collections import defaultdict
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta, date, time, timezone
from fastapi import HTTPException, status

from backend.database.connector import DatabaseConnector
from backend.schedule_doctors.models import (
    ShiftCreateRequestModel,
    MultiShiftBulkCreateRequestModel,
    ShiftTimeConfig,
    CalendarDayDTO,
    DayShiftDTO,
    DayUpsertRequest,
)

db = DatabaseConnector()

VN_TZ = timezone(timedelta(hours=7))
# ============================================================
# Helpers
# ============================================================

def _ensure_doctor_exists(doctor_id: int) -> None:
    row = db.query_one("SELECT id FROM doctors WHERE id=%s", (doctor_id,))
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bác sĩ")

def _ensure_doctor_assigned_to_clinic(doctor_id: int, clinic_id: int) -> None:
    row = db.query_one(
        """
        SELECT 1
        FROM clinic_doctor_assignments
        WHERE doctor_id=%s AND clinic_id=%s
        LIMIT 1
        """,
        (doctor_id, clinic_id),
    )
    if not row:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bác sĩ chưa được gán vào phòng khám này")

def _get_doctor_id_by_user(user_id: int) -> int:
    row = db.query_one("SELECT id FROM doctors WHERE user_id=%s", (user_id,))
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bác sĩ ứng với user")
    return int(row["id"])

def _extract_user_id(current_user: Any) -> int:
    if isinstance(current_user, dict):
        uid = current_user.get("user_id", current_user.get("id"))
    else:
        uid = getattr(current_user, "user_id", getattr(current_user, "id", None))
    if not uid:
        raise HTTPException(status_code=401, detail="Token thiếu user_id")
    return int(uid)

def _expand_target_dates(start_date: date, end_date: date, weekdays: List[int]) -> List[date]:
    days: List[date] = []
    cur = start_date
    wd = set(weekdays)
    while cur <= end_date:
        if cur.weekday() in wd:
            days.append(cur)
        cur += timedelta(days=1)
    return days

def _payload_self_conflicts(shifts: List[ShiftTimeConfig]) -> List[str]:
    from collections import defaultdict
    cnt = defaultdict(int)
    for s in shifts:
        cnt[str(s.start_time)] += 1
    return [t for t, n in cnt.items() if n > 1]

def _fetch_existing_shifts(doctor_id: int, clinic_id: int, target_dates: List[date]) -> Dict[str, Set[str]]:
    if not target_dates:
        return {}
    placeholders = ",".join(["%s"] * len(target_dates))
    sql = f"""
        SELECT work_date, CAST(start_time AS CHAR(8)) AS start_time
        FROM doctor_schedules
        WHERE doctor_id=%s AND clinic_id=%s
          AND work_date IN ({placeholders})
    """
    rows = db.query_get(sql, (doctor_id, clinic_id, *target_dates))
    result: Dict[str, Set[str]] = defaultdict(set)
    for r in rows:
        d = str(r["work_date"])
        result[d].add(r["start_time"])
    return result

# ============================================================
# Create single shift
# ============================================================

def create_shift(payload: ShiftCreateRequestModel) -> Dict[str, Any]:
    _ensure_doctor_exists(payload.doctor_id)
    _ensure_doctor_assigned_to_clinic(payload.doctor_id, payload.clinic_id)

    try:
        sched_id = db.execute_returning_id(
            """
            INSERT INTO doctor_schedules
                (doctor_id, clinic_id, work_date, start_time, end_time,
                 avg_minutes_per_patient, max_patients, status, note)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                payload.doctor_id,
                payload.clinic_id,
                payload.work_date,
                payload.start_time,
                payload.end_time,
                payload.avg_minutes_per_patient,
                payload.max_patients,
                payload.status,
                payload.note,
            ),
        )

        row = db.query_one(
            """
            SELECT id, doctor_id, clinic_id, work_date,
                   CAST(start_time AS CHAR(8)) AS start_time,
                   CAST(end_time   AS CHAR(8)) AS end_time,
                   avg_minutes_per_patient, max_patients, booked_patients,
                   status, note
            FROM doctor_schedules
            WHERE id=%s
            """,
            (sched_id,),
        )
        if not row:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Không đọc được ca vừa tạo")
        return row

    except pymysql.err.IntegrityError as ie:
        code = ie.args[0] if ie.args else None
        if code == 1062:   # duplicate
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Ca đã tồn tại")
        if code == 1452:   # FK
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="doctor_id/clinic_id không hợp lệ")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Lỗi ràng buộc CSDL")

    # ---- Một số connector bọc lỗi vào Exception chung -> soi message để map ngắn gọn
    except Exception as e:
        msg = repr(e)
        if "1062" in msg or "Duplicate entry" in msg:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Ca đã tồn tại")
        if "1452" in msg:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="doctor_id/clinic_id không hợp lệ")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi cơ sở dữ liệu")

def create_shift_for_doctor(doctor_id: int, payload: ShiftCreateRequestModel) -> Dict[str, Any]:
    _ensure_doctor_exists(doctor_id)
    _ensure_doctor_assigned_to_clinic(doctor_id, payload.clinic_id)
    fixed = payload.copy(update={"doctor_id": doctor_id})
    return create_shift(fixed)

def create_shift_for_user(current_user: Any, payload: ShiftCreateRequestModel) -> Dict[str, Any]:
    user_id = _extract_user_id(current_user)
    doctor_id = _get_doctor_id_by_user(user_id)
    return create_shift_for_doctor(doctor_id, payload)

# ============================================================
# Bulk create shifts (STRICT)
# ============================================================

def bulk_create_shifts(payload: MultiShiftBulkCreateRequestModel) -> Dict[str, int]:
    if payload.start_date > payload.end_date:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "start_date phải <= end_date")

    _ensure_doctor_exists(payload.doctor_id)
    _ensure_doctor_assigned_to_clinic(payload.doctor_id, payload.clinic_id)

    dup_in_payload = _payload_self_conflicts(payload.shifts)
    if dup_in_payload:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"message": "Trùng giờ trong payload",
                    "conflicts": [{"work_date": "multiple_in_payload", "start_time": t} for t in dup_in_payload]},
        )

    target_dates = _expand_target_dates(payload.start_date, payload.end_date, payload.weekdays)
    if not target_dates:
        return {"created": 0, "skipped_duplicates": 0}

    existed = _fetch_existing_shifts(payload.doctor_id, payload.clinic_id, target_dates)

    conflicts: List[Dict[str, str]] = []
    for d in target_dates:
        d_str = str(d)
        existed_times = existed.get(d_str, set())
        for s in payload.shifts:
            if str(s.start_time) in existed_times:
                conflicts.append({"work_date": d_str, "start_time": str(s.start_time)})

    if conflicts:
        raise HTTPException(status.HTTP_409_CONFLICT, detail={"message": "Ca đã tồn tại", "conflicts": conflicts})

    created = 0
    cur_date = payload.start_date
    while cur_date <= payload.end_date:
        if cur_date.weekday() in payload.weekdays:
            for s in payload.shifts:
                create_shift(
                    ShiftCreateRequestModel(
                        doctor_id=payload.doctor_id,
                        clinic_id=payload.clinic_id,
                        work_date=cur_date,
                        start_time=s.start_time,
                        end_time=s.end_time,
                        avg_minutes_per_patient=s.avg_minutes_per_patient,
                        max_patients=s.max_patients,
                        status=s.status,
                        note=s.note,
                    )
                )
                created += 1
        cur_date += timedelta(days=1)

    return {"created": created, "skipped_duplicates": 0}

# ============================================================
# Calendar & day shifts (read-only)
# ============================================================

def get_calendar_days(doctor_id: int, clinic_id: int, month: str) -> List[CalendarDayDTO]:
    """
    Trả về các ngày trong tháng có ca và còn chỗ (status=1),
    chỉ tính từ HÔM NAY trở đi theo múi giờ VN (+7).
    """
    try:
        start = datetime.strptime(month + "-01", "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "month phải dạng YYYY-MM")

    # ngày cuối tháng
    end = (date(start.year + (start.month == 12),
                1 if start.month == 12 else start.month + 1, 1) - timedelta(days=1))

    # Ngày hiện tại theo VN
    vn_today = datetime.now(VN_TZ).date()

    rows = db.query_get(
        """
        SELECT ds.work_date,
               COUNT(ds.id) AS shifts_count,
               SUM(ds.max_patients) AS total_capacity,
               SUM(ds.booked_patients) AS total_booked,
               SUM(GREATEST(ds.max_patients - ds.booked_patients, 0)) AS total_remaining
        FROM doctor_schedules ds
        WHERE ds.doctor_id = %s
          AND ds.clinic_id = %s
          AND ds.work_date BETWEEN %s AND %s
          AND ds.work_date >= %s           -- loại các ngày đã qua theo VN
          AND ds.status = 1
        GROUP BY ds.work_date
        HAVING total_remaining > 0
        ORDER BY ds.work_date
        """,
        (doctor_id, clinic_id, start, end, vn_today),
    )
    return [CalendarDayDTO(**r) for r in rows]


def get_day_shifts(doctor_id: int, clinic_id: int, work_date: date) -> List[DayShiftDTO]:
    """
    Trả về danh sách ca của 1 ngày theo múi giờ VN:
    - Nếu work_date là str -> ép kiểu 'YYYY-MM-DD'
    - Nếu work_date < hôm nay (VN) -> 404
    - Nếu work_date = hôm nay (VN) -> chỉ trả ca chưa kết thúc (end_time > VN now)
    - Nếu work_date > hôm nay (VN) -> trả toàn bộ ca status=1
    """
    # Ép kiểu khi router truyền chuỗi
    if isinstance(work_date, str):
        try:
            work_date = datetime.strptime(work_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "work_date phải dạng YYYY-MM-DD")

    vn_now = datetime.now(VN_TZ)
    vn_today = vn_now.date()
    vn_time_now: time = vn_now.time()

    # Ngày đã qua theo VN
    if work_date < vn_today:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không có ca khả dụng cho ngày này")

    # Hôm nay -> lọc ca chưa kết thúc
    if work_date == vn_today:
        rows = db.query_get(
            """
            SELECT id AS schedule_id,
                   CAST(start_time AS CHAR(8)) AS start_time,
                   CAST(end_time   AS CHAR(8)) AS end_time,
                   avg_minutes_per_patient, max_patients, booked_patients,
                   (max_patients - booked_patients) AS remaining,
                   status, note
            FROM doctor_schedules
            WHERE doctor_id = %s
              AND clinic_id = %s
              AND work_date = %s
              AND status = 1
              AND end_time > %s
            ORDER BY start_time
            """,
            (doctor_id, clinic_id, work_date, vn_time_now),
        )
    else:
        # Ngày tương lai -> không cần lọc theo giờ
        rows = db.query_get(
            """
            SELECT id AS schedule_id,
                   CAST(start_time AS CHAR(8)) AS start_time,
                   CAST(end_time   AS CHAR(8)) AS end_time,
                   avg_minutes_per_patient, max_patients, booked_patients,
                   (max_patients - booked_patients) AS remaining,
                   status, note
            FROM doctor_schedules
            WHERE doctor_id = %s
              AND clinic_id = %s
              AND work_date = %s
              AND status = 1
            ORDER BY start_time
            """,
            (doctor_id, clinic_id, work_date),
        )

    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không có ca khả dụng cho ngày này")

    return [DayShiftDTO(**r) for r in rows]

# ============================================================
# UPDATE/DELETE THEO schedule_id
# ============================================================

def update_day_shifts_for_doctor(doctor_id: int, payload: DayUpsertRequest) -> Dict[str, Any]:
    """
    UPDATE nhiều ca trong 1 ngày theo schedule_id.
    - Giới hạn trong (doctor_id, clinic_id, work_date).
    - Chỉ cập nhật các field có gửi; set updated_at = NOW().
    - Nếu đổi start_time đụng UNIQUE -> 409.
    """
    _ensure_doctor_exists(doctor_id)
    _ensure_doctor_assigned_to_clinic(doctor_id, payload.clinic_id)

    updated = 0
    missing: List[int] = []

    for s in payload.shifts:
        set_clauses: List[str] = []
        values: List[Any] = []

        if s.start_time is not None:
            set_clauses.append("start_time = %s")
            values.append(s.start_time)
        if s.end_time is not None:
            set_clauses.append("end_time = %s")
            values.append(s.end_time)
        if s.avg_minutes_per_patient is not None:
            set_clauses.append("avg_minutes_per_patient = %s")
            values.append(s.avg_minutes_per_patient)
        if s.max_patients is not None:
            set_clauses.append("max_patients = %s")
            values.append(s.max_patients)
        if s.status is not None:
            set_clauses.append("status = %s")
            values.append(s.status)
        if s.note is not None:
            set_clauses.append("note = %s")
            values.append(s.note)

        if not set_clauses:
            continue

        set_clauses.append("updated_at = NOW()")
        sql = f"""
            UPDATE doctor_schedules
               SET {", ".join(set_clauses)}
             WHERE id = %s
               AND doctor_id = %s
               AND clinic_id = %s
               AND work_date = %s
        """
        values.extend([s.schedule_id, doctor_id, payload.clinic_id, payload.work_date])

        try:
            rowcount = db.query_put(sql, tuple(values))
            if rowcount and rowcount > 0:
                updated += rowcount
            else:
                missing.append(s.schedule_id)
        except pymysql.err.IntegrityError as ie:
            if ie.args and ie.args[0] == 1062:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail=f"Trùng ca: start_time mới đã tồn tại trong ngày {payload.work_date}.",
                )
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"DB integrity error: {repr(ie)}")
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {repr(e)}")

    return {"message": "Cập nhật ca trong ngày thành công", "updated": updated, "missing_schedule_ids": missing}

def update_day_shifts_for_user(current_user: Any, payload: DayUpsertRequest) -> Dict[str, Any]:
    user_id = _extract_user_id(current_user)
    doctor_id = _get_doctor_id_by_user(user_id)
    return update_day_shifts_for_doctor(doctor_id, payload)

def delete_shifts_by_ids_for_doctor(doctor_id: int, clinic_id: int, schedule_ids: List[int]) -> Dict[str, int]:
    _ensure_doctor_exists(doctor_id)
    _ensure_doctor_assigned_to_clinic(doctor_id, clinic_id)
    if not schedule_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="schedule_ids rỗng")
    placeholders = ",".join(["%s"] * len(schedule_ids))
    sql = f"""
        DELETE FROM doctor_schedules
        WHERE doctor_id=%s AND clinic_id=%s
          AND id IN ({placeholders})
    """
    try:
        affected = db.query_put(sql, (doctor_id, clinic_id, *schedule_ids))
        return {"deleted": affected or 0}
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {repr(e)}")

def delete_shifts_by_ids_for_user(current_user: Any, clinic_id: int, schedule_ids: List[int]) -> Dict[str, int]:
    user_id = _extract_user_id(current_user)
    doctor_id = _get_doctor_id_by_user(user_id)
    return delete_shifts_by_ids_for_doctor(doctor_id, clinic_id, schedule_ids)

# ============================================================
# Admin wrapper cho bulk theo path doctor_id
# ============================================================

def bulk_create_shifts_for_doctor(doctor_id: int, payload: MultiShiftBulkCreateRequestModel) -> Dict[str, int]:
    _ensure_doctor_exists(doctor_id)
    _ensure_doctor_assigned_to_clinic(doctor_id, payload.clinic_id)
    fixed = payload.copy(update={"doctor_id": doctor_id})
    return bulk_create_shifts(fixed)
