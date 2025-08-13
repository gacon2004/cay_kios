from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from typing import Dict, Any
from backend.appointments.models import (
    BookByShiftRequestModel,
    AppointmentFilterModel,
)
from datetime import datetime, timedelta, timezone
import base64, qrcode
from io import BytesIO

db = DatabaseConnector()

# ================= QR =================
def _gen_qr_base64(payload: dict) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(payload); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# múi giờ VN để chọn ca offline
VN_TZ = timezone(timedelta(hours=7))

# ================= CORE BOOKING (online/offline đều dùng) =================
def _book_by_shift_core(
    patient_id: int,
    req: BookByShiftRequestModel,
    *,
    has_insurances: bool,
    channel: str,  # "online" | "offline"
) -> dict:
    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()

            # 0) Lấy & khóa ca
            cur.execute("""
              SELECT id, doctor_id, clinic_id, work_date, start_time, end_time,
                     avg_minutes_per_patient, max_patients, booked_patients, status
              FROM doctor_schedules
              WHERE id=%s AND doctor_id=%s AND clinic_id=%s AND status=1
              FOR UPDATE
            """, (req.schedule_id, req.doctor_id, req.clinic_id))
            ds = cur.fetchone()
            if not ds:
                raise HTTPException(404, "Không tìm thấy ca hợp lệ")

            # 0.1) Chặn đặt trùng ca cho cùng bệnh nhân
            cur.execute("""
              SELECT id FROM appointments
              WHERE patient_id=%s AND schedule_id=%s AND status IN (0,1,2)
              LIMIT 1
            """, (patient_id, req.schedule_id))
            dup = cur.fetchone()
            if dup:
                raise HTTPException(409, "Bạn đã đặt lịch cho ca này rồi")

            if ds["booked_patients"] >= ds["max_patients"]:
                raise HTTPException(409, "Ca đã hết chỗ")

            # 1) Giá dịch vụ (snapshot)
            price_row = db.query_one("SELECT price FROM services WHERE id=%s", (req.service_id,))
            if not price_row:
                raise HTTPException(404, "Không tìm thấy dịch vụ")
            base_price = float(price_row["price"])
            cur_price = base_price / 2 if has_insurances else base_price

            # 2) STT toàn ngày (theo clinic)
            cur.execute("""
              INSERT INTO clinic_daily_counters (clinic_id, counter_date, last_number)
              VALUES (%s, CURDATE(), 1)
              ON DUPLICATE KEY UPDATE last_number = last_number + 1
            """, (req.clinic_id,))
            cur.execute("""
              SELECT last_number FROM clinic_daily_counters
              WHERE clinic_id=%s AND counter_date=CURDATE() FOR UPDATE
            """, (req.clinic_id,))
            queue_number = cur.fetchone()["last_number"]

            # 3) STT trong ca
            cur.execute("""
              INSERT INTO doctor_shift_counters (schedule_id, last_number)
              VALUES (%s, 1)
              ON DUPLICATE KEY UPDATE last_number = last_number + 1
            """, (req.schedule_id,))
            cur.execute("""
              SELECT last_number FROM doctor_shift_counters
              WHERE schedule_id=%s FOR UPDATE
            """, (req.schedule_id,))
            shift_number = cur.fetchone()["last_number"]

            # 4) estimated_time
            # PyMySQL trả TIME thành timedelta -> convert sang phút
            start_td = ds["start_time"]
            start_minutes = int(start_td.total_seconds() // 60)
            offset_min = (shift_number - 1) * int(ds["avg_minutes_per_patient"])
            estimated_time = datetime(
                ds["work_date"].year, ds["work_date"].month, ds["work_date"].day,
                start_minutes // 60, start_minutes % 60
            ) + timedelta(minutes=offset_min)

            # 5) INSERT appointment
            cur.execute("""
              INSERT INTO appointments
                (patient_id, clinic_id, service_id, doctor_id, schedule_id,
                 queue_number, shift_number, estimated_time, printed, status,
                 booking_channel, cur_price)
              VALUES (%s,%s,%s,%s,%s, %s,%s,%s, 0, 1, %s, %s)
            """, (
                patient_id, req.clinic_id, req.service_id, req.doctor_id, req.schedule_id,
                queue_number, shift_number, estimated_time.replace(tzinfo=None),
                channel, cur_price
            ))
            appt_id = cur.lastrowid

            # 6) Giữ chỗ ca
            cur.execute("""
              UPDATE doctor_schedules
              SET booked_patients = booked_patients + 1
              WHERE id=%s AND booked_patients < max_patients
            """, (req.schedule_id,))
            if cur.rowcount == 0:
                raise HTTPException(409, "Ca vừa hết chỗ")

            # 7) QR
            qr_b64 = _gen_qr_base64({
                "appointment_id": appt_id,
                "queue": queue_number,
                "shift": shift_number,
                "estimated": estimated_time.isoformat(),
                "has_insurances": has_insurances,
                "channel": channel
            })
            cur.execute("UPDATE appointments SET qr_code=%s WHERE id=%s", (qr_b64, appt_id))

            # 8) Trả chi tiết
            cur.execute("""
                SELECT a.*, s.name AS service_name, s.price AS service_price,
                       d.full_name AS doctor_name, c.name AS clinic_name
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                JOIN doctors  d ON a.doctor_id = d.id
                JOIN clinics  c ON a.clinic_id = c.id
                WHERE a.id = %s
            """, (appt_id,))
            row = cur.fetchone()
            conn.commit()
            row["qr_code"] = qr_b64
            return row

    except HTTPException:
        try: conn.rollback()
        except: pass
        raise
    except Exception as e:
        try: conn.rollback()
        except: pass
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {e}")

# ================= OFFLINE: tự chọn ca nếu chưa có schedule_id =================
def _pick_schedule_for_offline(cur, clinic_id: int, doctor_id: int, *, today, now_time):
    """
    Trả về bản ghi ca phù hợp:
    - ưu tiên ca đang diễn ra (start<=now<end) còn chỗ
    - nếu không có, lấy ca sắp tới gần nhất hôm nay còn chỗ
    - nếu không có, trả None
    """
    # 1) Ca đang diễn ra
    cur.execute("""
        SELECT id, doctor_id, clinic_id, work_date, start_time, end_time,
               avg_minutes_per_patient, max_patients, booked_patients, status
        FROM doctor_schedules
        WHERE clinic_id=%s
          AND doctor_id=%s
          AND DATE(work_date)=%s
          AND status=1
          AND booked_patients < max_patients
          AND start_time <= %s AND %s < end_time
        ORDER BY start_time
        LIMIT 1
    """, (clinic_id, doctor_id, today, now_time, now_time))
    ds = cur.fetchone()
    if ds:
        return ds

    # 2) Ca sắp tới gần nhất
    cur.execute("""
        SELECT id, doctor_id, clinic_id, work_date, start_time, end_time,
               avg_minutes_per_patient, max_patients, booked_patients, status
        FROM doctor_schedules
        WHERE clinic_id=%s
          AND doctor_id=%s
          AND DATE(work_date)=%s
          AND status=1
          AND booked_patients < max_patients
          AND start_time > %s
        ORDER BY start_time
        LIMIT 1
    """, (clinic_id, doctor_id, today, now_time))
    return cur.fetchone()

# ================= PUBLIC API =================
def book_by_shift_online(patient_id: int, req: BookByShiftRequestModel, has_insurances: bool) -> dict:
    # KHÔNG thay đổi logic online
    return _book_by_shift_core(patient_id, req, has_insurances=has_insurances, channel="online")

def book_by_shift_offline(patient_id: int, req: BookByShiftRequestModel, has_insurances: bool) -> dict:
    """
    Nếu client gửi sẵn schedule_id -> giữ nguyên core.
    Nếu KHÔNG, tự tìm ca phù hợp theo thời gian VN của hôm nay tại clinic/doctor đã chọn.
    """
    if getattr(req, "schedule_id", None):
        return _book_by_shift_core(patient_id, req, has_insurances=has_insurances, channel="offline")

    # cần clinic_id & doctor_id để chọn ca
    if not getattr(req, "clinic_id", None) or not getattr(req, "doctor_id", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Thiếu clinic_id hoặc doctor_id")

    now_vn = datetime.now(VN_TZ)
    today = now_vn.date()
    now_time = now_vn.time()

    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()
            ds = _pick_schedule_for_offline(
                cur,
                clinic_id=req.clinic_id,
                doctor_id=req.doctor_id,
                today=today,
                now_time=now_time,
            )
            if not ds:
                raise HTTPException(status.HTTP_409_CONFLICT, "Hôm nay đã hết ca, vui lòng chọn ngày khác")

            # gán schedule_id rồi dùng core để đảm bảo mọi ràng buộc/lock
            req.schedule_id = ds["id"]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {e}")

    # gọi core (sẽ lock lại ca bằng FOR UPDATE và kiểm tra full/trùng)
    return _book_by_shift_core(patient_id, req, has_insurances=has_insurances, channel="offline")

# ================= QUERY MY APPOINTMENTS =================
def get_my_appointments(patient_id: int, filters: AppointmentFilterModel):
    where = ["a.patient_id = %s"]
    params: list = [patient_id]

    if filters.from_date:
        where.append("DATE(a.estimated_time) >= %s")
        params.append(filters.from_date)
    if filters.to_date:
        where.append("DATE(a.estimated_time) <= %s")
        params.append(filters.to_date)
    if filters.status_filter is not None:
        where.append("a.status = %s")
        params.append(filters.status_filter)

    sql = f"""
        SELECT a.*,
               s.name  AS service_name,
               s.price AS service_price,
               d.full_name AS doctor_name,
               c.name AS clinic_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN doctors  d ON a.doctor_id = d.id
        JOIN clinics  c ON a.clinic_id = c.id
        WHERE {" AND ".join(where)}
        -- estimated_time nếu có; nếu NULL thì dùng created_at cho ổn định
        ORDER BY COALESCE(a.estimated_time, a.created_at) DESC, a.id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])
    return db.query_get(sql, tuple(params))

# ================= CANCEL BY PATIENT =================
def cancel_my_appointment(appointment_id: int, patient_id: int) -> dict:
    """
    Bệnh nhân hủy lịch của chính mình:
    - lock appointment
    - chỉ cho hủy khi status cho phép (ví dụ 1=confirmed)
    - set status=4 (canceled)
    - giảm booked_patients của doctor_schedules tương ứng (không âm)
    """
    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()

            # 1) Lock bản ghi hẹn
            cur.execute("""
                SELECT id, patient_id, schedule_id, status
                FROM appointments
                WHERE id=%s AND patient_id=%s
                FOR UPDATE
            """, (appointment_id, patient_id))
            appt = cur.fetchone()
            if not appt:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy lịch hẹn")

            # 2) Chặn hủy nếu không còn hiệu lực
            if appt["status"] not in (1,):  # 1 = confirmed
                raise HTTPException(status.HTTP_409_CONFLICT, "Trạng thái hiện tại không cho phép hủy")

            # 3) Cập nhật trạng thái -> canceled
            cur.execute("UPDATE appointments SET status=4 WHERE id=%s", (appointment_id,))

            # 4) Giảm booked_patients của ca (nếu có schedule_id)
            if appt["schedule_id"]:
                cur.execute("""
                    UPDATE doctor_schedules
                    SET booked_patients = GREATEST(booked_patients - 1, 0)
                    WHERE id=%s
                """, (appt["schedule_id"],))

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
