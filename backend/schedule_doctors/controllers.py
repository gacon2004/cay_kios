import pymysql
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from fastapi import HTTPException, status

from backend.database.connector import DatabaseConnector
from backend.schedule_doctors.models import (
    ShiftCreateRequestModel,
    MultiShiftBulkCreateRequestModel,
    CalendarDayDTO,
    DayShiftDTO,
)

db = DatabaseConnector()

# ===== Tạo 1 ca, dùng execute_returning_id + query_one =====
def create_shift(payload: ShiftCreateRequestModel) -> Dict[str, Any]:
    try:
        sched_id = db.execute_returning_id(
            """
            INSERT INTO doctor_schedules
                (doctor_id, clinic_id, work_date, start_time, end_time,
                 avg_minutes_per_patient, max_patients, status, note)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                payload.doctor_id, payload.clinic_id, payload.work_date,
                payload.start_time, payload.end_time,
                payload.avg_minutes_per_patient, payload.max_patients,
                payload.status, payload.note,
            ),
        )

        # Trả về record, CAST TIME -> 'HH:MM:SS'
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
            raise HTTPException(500, "Không đọc được ca vừa tạo")
        return row

    except Exception as e:
        # Bắt duplicate key (1062) -> 409
        if isinstance(e, pymysql.err.IntegrityError) and getattr(e, "args", [None])[0] == 1062:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ca đã tồn tại (trùng doctor_id/clinic_id/work_date/start_time)",
            )
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {e}")

# ===== Bulk: tạo nhiều ca/ngày; bỏ qua trùng và thống kê =====
def bulk_create_shifts(payload: MultiShiftBulkCreateRequestModel) -> Dict[str, int]:
    if payload.start_date > payload.end_date:
        raise HTTPException(400, "start_date phải <= end_date")

    created = 0
    skipped = 0
    cur_date = payload.start_date
    one_day = timedelta(days=1)

    while cur_date <= payload.end_date:
        if cur_date.weekday() in payload.weekdays:
            for s in payload.shifts:
                try:
                    create_shift(ShiftCreateRequestModel(
                        doctor_id=payload.doctor_id,
                        clinic_id=payload.clinic_id,
                        work_date=cur_date,
                        start_time=s.start_time,
                        end_time=s.end_time,
                        avg_minutes_per_patient=s.avg_minutes_per_patient,
                        max_patients=s.max_patients,
                        status=s.status,
                        note=s.note
                    ))
                    created += 1
                except HTTPException as ex:
                    if ex.status_code == 409:
                        skipped += 1
                    else:
                        raise
        cur_date += one_day

    return {"created": created, "skipped_duplicates": skipped}

# ===== Calendar: ngày trong tháng còn chỗ =====
def get_calendar_days(doctor_id: int, clinic_id: int, month: str) -> List[CalendarDayDTO]:
    try:
        start = datetime.strptime(month + "-01", "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "month phải dạng YYYY-MM")
    end = (date(start.year + (start.month == 12), 1 if start.month == 12 else start.month + 1, 1)
           - timedelta(days=1))

    rows = db.query_get(
        """
        SELECT ds.work_date,
               COUNT(ds.id) AS shifts_count,
               SUM(ds.max_patients) AS total_capacity,
               SUM(ds.booked_patients) AS total_booked,
               SUM(GREATEST(ds.max_patients - ds.booked_patients, 0)) AS total_remaining
        FROM doctor_schedules ds
        WHERE ds.doctor_id=%s AND ds.clinic_id=%s
          AND ds.work_date BETWEEN %s AND %s
          AND ds.status=1
        GROUP BY ds.work_date
        HAVING total_remaining > 0
        ORDER BY ds.work_date
        """,
        (doctor_id, clinic_id, start, end),
    )
    return [CalendarDayDTO(**r) for r in rows]

# ===== Danh sách ca trong ngày (nếu rỗng -> 404) =====
def get_day_shifts(doctor_id: int, clinic_id: int, work_date: date) -> List[DayShiftDTO]:
    rows = db.query_get(
        """
        SELECT id AS schedule_id,
               CAST(start_time AS CHAR(8)) AS start_time,
               CAST(end_time   AS CHAR(8)) AS end_time,
               avg_minutes_per_patient, max_patients, booked_patients,
               (max_patients - booked_patients) AS remaining,
               status, note
        FROM doctor_schedules
        WHERE doctor_id=%s AND clinic_id=%s AND work_date=%s AND status=1
        ORDER BY start_time
        """,
        (doctor_id, clinic_id, work_date),
    )
    if not rows:
        raise HTTPException(404, "Không có ca làm việc cho bác sĩ/phòng khám vào ngày này")
    return [DayShiftDTO(**r) for r in rows]
