from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from typing import Dict, Any, List
from backend.appointments.models import (
    BookByShiftRequestModel,
    AppointmentFilterModel,
)
from datetime import datetime, timedelta, timezone

db = DatabaseConnector()
VN_TZ = timezone(timedelta(hours=7))

def _book_by_shift_core(
    patient_id: int,
    req: BookByShiftRequestModel,
    *, has_insurances: bool, channel: str  # "online" | "offline"
) -> dict:
    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()

            # 0) Lấy & khóa ca
            cur.execute(
                """
                SELECT id, doctor_id, clinic_id, work_date, start_time, end_time,
                       avg_minutes_per_patient, max_patients, booked_patients, status
                FROM doctor_schedules
                WHERE id=%s AND doctor_id=%s AND clinic_id=%s AND status=1
                FOR UPDATE
                """,
                (req.schedule_id, req.doctor_id, req.clinic_id),
            )
            ds = cur.fetchone()
            if not ds:
                raise HTTPException(404, "Không tìm thấy ca hợp lệ")

            # 0.1) Chặn ca quá khứ (theo VN)
            now_vn = datetime.now(VN_TZ)
            work_date = ds["work_date"]               # date/datetime
            end_td = ds["end_time"]                   # TIME -> timedelta
            end_minutes = int(end_td.total_seconds() // 60)
            end_dt_vn = datetime(
                work_date.year, work_date.month, work_date.day,
                end_minutes // 60, end_minutes % 60, tzinfo=VN_TZ
            )
            if work_date < now_vn.date() or (work_date == now_vn.date() and end_dt_vn <= now_vn):
                raise HTTPException(status.HTTP_409_CONFLICT, "Ca đã qua, vui lòng chọn ca khác")

            # 0.2) Chặn đặt trùng ca cho cùng bệnh nhân
            cur.execute(
                """
                SELECT id FROM appointments
                WHERE patient_id=%s AND schedule_id=%s AND status IN (0,1,2)
                LIMIT 1
                """,
                (patient_id, req.schedule_id),
            )
            if cur.fetchone():
                raise HTTPException(409, "Bạn đã đặt lịch cho ca này rồi")

            if ds["booked_patients"] >= ds["max_patients"]:
                raise HTTPException(409, "Ca đã hết chỗ")

            # 1) Giá dịch vụ (snapshot)
            price_row = db.query_one(
                "SELECT price FROM services WHERE id=%s", (req.service_id,)
            )
            if not price_row:
                raise HTTPException(404, "Không tìm thấy dịch vụ")
            base_price = float(price_row["price"])
            cur_price = base_price / 2 if has_insurances else base_price

            # 2) STT toàn ngày (theo clinic)
            cur.execute(
                """
                INSERT INTO clinic_daily_counters (clinic_id, counter_date, last_number)
                VALUES (%s, CURDATE(), 1)
                ON DUPLICATE KEY UPDATE last_number = last_number + 1
                """,
                (req.clinic_id,),
            )
            cur.execute(
                """
                SELECT last_number FROM clinic_daily_counters
                WHERE clinic_id=%s AND counter_date=CURDATE() FOR UPDATE
                """,
                (req.clinic_id,),
            )
            queue_number = cur.fetchone()["last_number"]

            # 3) STT trong ca
            cur.execute(
                """
                INSERT INTO doctor_shift_counters (schedule_id, last_number)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE last_number = last_number + 1
                """,
                (req.schedule_id,),
            )
            cur.execute(
                "SELECT last_number FROM doctor_shift_counters WHERE schedule_id=%s FOR UPDATE",
                (req.schedule_id,),
            )
            shift_number = cur.fetchone()["last_number"]

            # 4) estimated_time
            start_td = ds["start_time"]                       # timedelta
            start_minutes = int(start_td.total_seconds() // 60)
            offset_min = (shift_number - 1) * int(ds["avg_minutes_per_patient"])
            estimated_time = datetime(
                work_date.year, work_date.month, work_date.day,
                start_minutes // 60, start_minutes % 60,
            ) + timedelta(minutes=offset_min)

            # 5) INSERT appointment (KHÔNG còn qr_code)
            cur.execute(
                """
                INSERT INTO appointments
                    (patient_id, clinic_id, service_id, doctor_id, schedule_id,
                     queue_number, shift_number, estimated_time, printed, status,
                     booking_channel, cur_price)
                VALUES (%s,%s,%s,%s,%s, %s,%s,%s, 0, 1, %s, %s)
                """,
                (
                    patient_id, req.clinic_id, req.service_id, req.doctor_id, req.schedule_id,
                    queue_number, shift_number, estimated_time, channel, cur_price,
                ),
            )
            appt_id = cur.lastrowid

            # 6) Giữ chỗ ca
            cur.execute(
                """
                UPDATE doctor_schedules
                SET booked_patients = booked_patients + 1
                WHERE id=%s AND booked_patients < max_patients
                """,
                (req.schedule_id,),
            )
            if cur.rowcount == 0:
                raise HTTPException(409, "Ca vừa hết chỗ")

            # 7) Trả chi tiết (không chọn qr_code)
            cur.execute(
                """
                SELECT a.id, a.patient_id, a.clinic_id, a.service_id, a.doctor_id, a.schedule_id,
                       a.queue_number, a.shift_number, a.estimated_time, a.printed, a.status,
                       a.booking_channel, a.cur_price,
                       s.name  AS service_name, s.price AS service_price,
                       d.full_name AS doctor_name, c.name AS clinic_name
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                JOIN doctors  d ON a.doctor_id = d.id
                JOIN clinics  c ON a.clinic_id = c.id
                WHERE a.id = %s
                """,
                (appt_id,),
            )
            row = cur.fetchone()
            conn.commit()
            return row

    except HTTPException:
        try: conn.rollback()
        except: pass
        raise
    except Exception as e:
        try: conn.rollback()
        except: pass
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {e}")


def _pick_schedule_for_offline(cur, clinic_id: int, doctor_id: int, *, today, now_time):
    # Không đổi – chỉ chọn ca còn chỗ trong hôm nay
    cur.execute(
        """
        SELECT id, doctor_id, clinic_id, work_date, start_time, end_time,
               avg_minutes_per_patient, max_patients, booked_patients, status
        FROM doctor_schedules
        WHERE clinic_id=%s AND doctor_id=%s AND DATE(work_date)=%s
              AND status=1 AND booked_patients < max_patients
              AND start_time <= %s AND %s < end_time
        ORDER BY start_time LIMIT 1
        """,
        (clinic_id, doctor_id, today, now_time, now_time),
    )
    ds = cur.fetchone()
    if ds: return ds

    cur.execute(
        """
        SELECT id, doctor_id, clinic_id, work_date, start_time, end_time,
               avg_minutes_per_patient, max_patients, booked_patients, status
        FROM doctor_schedules
        WHERE clinic_id=%s AND doctor_id=%s AND DATE(work_date)=%s
              AND status=1 AND booked_patients < max_patients
              AND start_time > %s
        ORDER BY start_time LIMIT 1
        """,
        (clinic_id, doctor_id, today, now_time),
    )
    return cur.fetchone()


def book_by_shift_online(patient_id: int, req: BookByShiftRequestModel, has_insurances: bool) -> dict:
    return _book_by_shift_core(patient_id, req, has_insurances=has_insurances, channel="online")

def book_by_shift_offline(patient_id: int, req: BookByShiftRequestModel, has_insurances: bool) -> dict:
    if getattr(req, "schedule_id", None):
        return _book_by_shift_core(patient_id, req, has_insurances=has_insurances, channel="offline")

    if not getattr(req, "clinic_id", None) or not getattr(req, "doctor_id", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Thiếu clinic_id hoặc doctor_id")

    now_vn = datetime.now(VN_TZ)
    today, now_time = now_vn.date(), now_vn.time()

    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()
            ds = _pick_schedule_for_offline(cur, clinic_id=req.clinic_id, doctor_id=req.doctor_id,
                                            today=today, now_time=now_time)
            if not ds:
                raise HTTPException(status.HTTP_409_CONFLICT, "Hôm nay đã hết ca, vui lòng chọn ngày khác")
            req.schedule_id = ds["id"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {e}")

    return _book_by_shift_core(patient_id, req, has_insurances=has_insurances, channel="offline")


def get_my_appointments(patient_id: int, filters: AppointmentFilterModel):
    where = ["a.patient_id = %s"]
    params = [patient_id]
    if filters.from_date:
        where.append("DATE(a.estimated_time) >= %s"); params.append(filters.from_date)
    if filters.to_date:
        where.append("DATE(a.estimated_time) <= %s"); params.append(filters.to_date)
    if filters.status_filter is not None:
        where.append("a.status = %s"); params.append(filters.status_filter)

    sql = f"""
        SELECT a.id, a.patient_id, a.clinic_id, a.service_id, a.doctor_id, a.schedule_id,
               a.queue_number, a.shift_number, a.estimated_time, a.printed, a.status,
               a.booking_channel, a.cur_price,
               s.name AS service_name, s.price AS service_price,
               d.full_name AS doctor_name, c.name AS clinic_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN doctors  d ON a.doctor_id = d.id
        JOIN clinics  c ON a.clinic_id = c.id
        WHERE {" AND ".join(where)}
        ORDER BY COALESCE(a.estimated_time, a.created_at) DESC, a.id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])
    return db.query_get(sql, tuple(params))


def get_my_appointments_of_doctor_user(user_id: int) -> List[Dict[str, Any]]:
    sql = """
        SELECT
            a.id AS appointment_id,
            a.patient_id,
            p.full_name AS patient_name,
            p.phone AS patient_phone,
            a.clinic_id,
            c.name AS clinic_name,
            a.schedule_id,
            ds.work_date,
            TIME_FORMAT(ds.start_time, '%%H:%%i') AS start_time,
            TIME_FORMAT(ds.end_time,   '%%H:%%i') AS end_time,
            a.status AS appointment_status,
            a.created_at
        FROM appointments a
        JOIN doctors d              ON d.id = a.doctor_id
        LEFT JOIN doctor_schedules ds ON ds.id = a.schedule_id
        JOIN patients p             ON p.id = a.patient_id
        JOIN clinics c              ON c.id = a.clinic_id
        WHERE d.user_id = %s
        ORDER BY a.created_at DESC
    """
    return db.query_get(sql, (user_id,))


def cancel_my_appointment(appointment_id: int, patient_id: int) -> dict:
    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, patient_id, schedule_id, status FROM appointments WHERE id=%s AND patient_id=%s FOR UPDATE",
                (appointment_id, patient_id),
            )
            appt = cur.fetchone()
            if not appt:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy lịch hẹn")
            if appt["status"] not in (1,):
                raise HTTPException(status.HTTP_409_CONFLICT, "Trạng thái hiện tại không cho phép hủy")

            cur.execute("UPDATE appointments SET status=4 WHERE id=%s", (appointment_id,))
            if appt["schedule_id"]:
                cur.execute(
                    "UPDATE doctor_schedules SET booked_patients = GREATEST(booked_patients - 1, 0) WHERE id=%s",
                    (appt["schedule_id"],),
                )
            conn.commit()
            return {"message": "Hủy lịch hẹn thành công"}
    except HTTPException:
        try: conn.rollback()
        except: pass
        raise
    except Exception as e:
        try: conn.rollback()
        except: pass
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Lỗi cơ sở dữ liệu: {e}")
