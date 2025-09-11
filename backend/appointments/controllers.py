from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from typing import Dict, Any, List
from backend.appointments.models import (
    BookByShiftRequestModel,
    AppointmentFilterModel,
    AppointmentPaymentFilterModel
)
from datetime import datetime, timedelta, timezone

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from io import BytesIO
from pathlib import Path
from reportlab.lib import colors

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

def list_patient_appointments_by_payment(
    patient_id: int,
    filters: AppointmentPaymentFilterModel
) -> List[Dict[str, Any]]:
    where = ["a.patient_id = %s"]
    params: list = [patient_id]

    if filters.from_date:
        where.append("DATE(COALESCE(a.estimated_time, a.created_at)) >= %s")
        params.append(filters.from_date)
    if filters.to_date:
        where.append("DATE(COALESCE(a.estimated_time, a.created_at)) <= %s")
        params.append(filters.to_date)

    sql = f"""
        SELECT
            -- Thông tin bệnh nhân
            p.full_name      AS patient_name,
            p.national_id    AS patient_national_id,
            DATE_FORMAT(p.date_of_birth, '%%Y-%%m-%%d') AS patient_dob,
            p.gender         AS patient_gender,
            p.phone          AS patient_phone,

            -- Thông tin khám
            a.id             AS appointment_id,
            s.name           AS service_name,
            c.name           AS clinic_name,
            d.full_name      AS doctor_name,
            a.shift_number,
            a.queue_number,
            CAST(a.cur_price AS SIGNED) AS price_vnd,
            a.estimated_time,

            -- Thanh toán (bản ghi mới nhất)
            po.status        AS pay_status,
            po.paid_at,
            po.order_code
        FROM appointments a
        JOIN patients  p ON p.id = a.patient_id
        JOIN services  s ON s.id = a.service_id
        JOIN clinics   c ON c.id = a.clinic_id
        JOIN doctors   d ON d.id = a.doctor_id
        LEFT JOIN (
            SELECT t.*
            FROM payment_orders t
            JOIN (
                SELECT appointment_id, MAX(id) AS max_id
                FROM payment_orders
                GROUP BY appointment_id
            ) z ON z.max_id = t.id
        ) po ON po.appointment_id = a.id
        WHERE {" AND ".join(where)}
    """
    if filters.pay_status:
        sql += " AND po.status = %s "
        params.append(filters.pay_status.upper())

    sql += """
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

def update_appointment_status_by_doctor(user_id: int, appointment_id: int, new_status: int) -> dict:
    # Lấy doctor_id từ user_id
    doc = db.query_one("SELECT id FROM doctors WHERE user_id=%s", (user_id,))
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bác sĩ ứng với user")
    doctor_id = int(doc["id"])

    conn = db.get_connection()
    try:
        with conn:
            cur = conn.cursor()

            # Lock lịch hẹn
            cur.execute("""
                SELECT id, doctor_id, schedule_id, status
                FROM appointments
                WHERE id=%s
                FOR UPDATE
            """, (appointment_id,))
            appt = cur.fetchone()
            if not appt:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy lịch hẹn")

            if int(appt["doctor_id"]) != doctor_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Bạn không có quyền sửa lịch hẹn này")

            old_status = int(appt["status"])

            allowed = {1, 2, 3, 4}  # 1=confirmed, 2=completed, 3=no_show, 4=canceled
            if new_status not in allowed:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Trạng thái không hợp lệ")

            if new_status == old_status:
                return {"message": "Không có thay đổi", "old_status": old_status, "new_status": new_status}

            # Cập nhật trạng thái
            cur.execute("""
                UPDATE appointments
                SET status=%s, updated_at=NOW()
                WHERE id=%s
            """, (new_status, appointment_id))

            # Nếu hủy -> trả slot
            if new_status == 4 and appt["schedule_id"]:
                cur.execute("""
                    UPDATE doctor_schedules
                    SET booked_patients = GREATEST(booked_patients - 1, 0)
                    WHERE id=%s
                """, (appt["schedule_id"],))

            conn.commit()
            return {
                "message": "Cập nhật trạng thái thành công",
                "old_status": old_status,
                "new_status": new_status
            }

    except HTTPException:
        try: conn.rollback()
        except: pass
        raise
    except Exception as e:
        try: conn.rollback()
        except: pass
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi cơ sở dữ liệu: {e}")

def list_all_appointments_by_payment_admin(
    filters: AppointmentPaymentFilterModel
) -> List[Dict[str, Any]]:
    where = ["1=1"]
    params: list = []

    if filters.from_date:
        where.append("DATE(COALESCE(a.estimated_time, a.created_at)) >= %s")
        params.append(filters.from_date)
    if filters.to_date:
        where.append("DATE(COALESCE(a.estimated_time, a.created_at)) <= %s")
        params.append(filters.to_date)

    sql = f"""
        SELECT
            -- Bệnh nhân
            p.full_name      AS patient_name,
            p.national_id    AS patient_national_id,
            DATE_FORMAT(p.date_of_birth, '%%Y-%%m-%%d') AS patient_dob,
            p.gender         AS patient_gender,
            p.phone          AS patient_phone,

            -- Khám
            a.id             AS appointment_id,
            s.name           AS service_name,
            c.name           AS clinic_name,
            d.full_name      AS doctor_name,
            a.shift_number,
            a.queue_number,
            CAST(a.cur_price AS SIGNED) AS price_vnd,
            a.estimated_time,

            -- Thanh toán (bản ghi mới nhất)
            COALESCE(po.status, 'UNPAID') AS pay_status,
            po.paid_at,
            po.order_code

        FROM appointments a
        JOIN patients  p ON p.id = a.patient_id
        JOIN services  s ON s.id = a.service_id
        JOIN clinics   c ON c.id = a.clinic_id
        JOIN doctors   d ON d.id = a.doctor_id
        LEFT JOIN (
            SELECT t.*
            FROM payment_orders t
            JOIN (
                SELECT appointment_id, MAX(id) AS max_id
                FROM payment_orders
                GROUP BY appointment_id
            ) z ON z.max_id = t.id
        ) po ON po.appointment_id = a.id
        WHERE {" AND ".join(where)}
    """
    if filters.pay_status:
        sql += " AND COALESCE(po.status, 'UNPAID') = %s "
        params.append(filters.pay_status.upper())

    sql += """
        ORDER BY COALESCE(a.estimated_time, a.created_at) DESC, a.id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    return db.query_get(sql, tuple(params))


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

UI = {
    "title":        colors.HexColor("#0F172A"),
    "muted":        colors.HexColor("#64748B"),
    "patient_bg":   colors.HexColor("#EAF2FF"),
    "patient_bd":   colors.HexColor("#D6E3FF"),
    "exam_bg":      colors.HexColor("#F0FAF4"),
    "exam_bd":      colors.HexColor("#CDE7D6"),
    "chip_bg":      colors.HexColor("#E8F5E9"),
    "chip_bd":      colors.HexColor("#43A047"),
    "chip_txt":     colors.HexColor("#2E7D32"),
    "price":        colors.HexColor("#16A34A"),
    "danger":       colors.HexColor("#EF4444"),
    "hint_bg":      colors.HexColor("#FFF7D6"),
    "hint_bd":      colors.HexColor("#FDE68A"),
    "icon_green":   colors.HexColor("#10B981"),
}

# fonts
_FONTS_REGISTERED = False
def _ensure_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED: return
    fonts_dir = Path(__file__).resolve().parents[1] / "fonts"
    pdfmetrics.registerFont(TTFont("DejaVu",      str(fonts_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(fonts_dir / "DejaVuSans-Bold.ttf")))
    _FONTS_REGISTERED = True

# helpers
def _fmt_vnd(n: int | float) -> str:
    try: n = int(n)
    except: return str(n)
    return f"{n:,}".replace(",", ".") + " ₫"

def _qr_reader(payload: str) -> ImageReader:
    img = qrcode.make(payload)
    pil = img.get_image() if hasattr(img, "get_image") else img
    b = BytesIO(); pil.save(b, format="PNG"); b.seek(0)
    return ImageReader(b)

def _round_rect(cv, x, y_top, w, h, r, fill, stroke, lw=1):
    cv.setFillColor(fill); cv.setStrokeColor(stroke); cv.setLineWidth(lw)
    cv.roundRect(x, y_top - h, w, h, r, stroke=1, fill=1)

def _section_header(cv, x, y, text, dot_color):
    cv.setFillColor(dot_color); cv.circle(x + 2.2*mm, y - 2.6*mm, 1.6*mm, stroke=0, fill=1)
    cv.setFillColor(UI["title"]); cv.setFont("DejaVu-Bold", 12); cv.drawString(x + 6*mm, y, text)

def _pair(cv, x, y, label, value, label_w, value_w, *, value_bold=False, value_color=None):
    """
    Label & value đều căn trái. Giá trị bắt đầu tại:
        x + max(label_w, measured(label)+gap)
    -> tránh bị dính khi label dài.
    """
    lbl_font, lbl_size, gap = "DejaVu-Bold", 10, 2*mm
    cv.setFont(lbl_font, lbl_size); cv.setFillColor(UI["title"]); cv.drawString(x, y, label)
    measured = cv.stringWidth(label, lbl_font, lbl_size)
    value_x = x + max(label_w, measured + gap)
    cv.setFont("DejaVu-Bold" if value_bold else "DejaVu", 10)
    cv.setFillColor(value_color or UI["title"])
    cv.drawString(value_x, y, str(value))

# data
def _fetch_paid_appointment_for_print(appointment_id: int, patient_id: int) -> Dict[str, Any]:
    rows = db.query_get(
        """
        SELECT
            a.id, a.patient_id, a.clinic_id, a.service_id, a.doctor_id, a.schedule_id,
            a.queue_number, a.shift_number, a.estimated_time, a.status, a.cur_price,
            p.full_name AS patient_name, p.national_id,
            DATE_FORMAT(p.date_of_birth,'%%Y-%%m-%%d') AS dob,
            p.gender, p.phone,
            s.name AS service_name,
            d.full_name AS doctor_name,
            c.name AS clinic_name,
            po.order_code, po.status AS pay_status, po.paid_at, po.qr_code_url
        FROM appointments a
        JOIN patients  p ON p.id = a.patient_id
        JOIN services  s ON s.id = a.service_id
        JOIN doctors   d ON d.id = a.doctor_id
        JOIN clinics   c ON c.id = a.clinic_id
        LEFT JOIN (
            SELECT t.*
            FROM payment_orders t
            JOIN (SELECT appointment_id, MAX(id) AS max_id
                  FROM payment_orders GROUP BY appointment_id) z ON z.max_id = t.id
        ) po ON po.appointment_id = a.id
        WHERE a.id=%s AND a.patient_id=%s
        LIMIT 1
        """,
        (appointment_id, patient_id),
    )
    if not rows: raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy lịch hẹn")
    info = rows[0]
    if not info.get("order_code") or info.get("pay_status") != "PAID":
        raise HTTPException(status.HTTP_409_CONFLICT, "Lịch hẹn chưa thanh toán xong")
    return info

# render
def generate_visit_ticket_pdf(appointment_id: int, patient_id: int) -> tuple[bytes, str]:
    _ensure_fonts()
    data = _fetch_paid_appointment_for_print(appointment_id, patient_id)

    est = data.get("estimated_time")
    est_str  = est.strftime("%H:%M %d/%m/%Y") if isinstance(est, datetime) else "-"
    paid_at  = data.get("paid_at")
    paid_str = paid_at.strftime("%H:%M %d/%m/%Y") if isinstance(paid_at, datetime) else "-"

    buf = BytesIO()
    cv = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    margin = 16*mm
    content_w = w - 2*margin
    y = h - margin
    row = 6*mm

    # Title
    cv.setFont("DejaVu-Bold", 18); cv.setFillColor(UI["title"]); cv.drawCentredString(w/2, y, "Hoàn Thành Đăng Ký")
    y -= 7*mm
    cv.setFont("DejaVu", 11); cv.setFillColor(UI["muted"]); cv.drawCentredString(w/2, y, "Kiểm tra thông tin và in phiếu khám")
    y -= 10*mm

    # Card patient
    card1_h = 42*mm
    _round_rect(cv, margin, y, content_w, card1_h, 8, UI["patient_bg"], UI["patient_bd"])
    inner = 9*mm
    x = margin + inner
    y1 = y - inner
    _section_header(cv, x, y1, "Thông Tin Bệnh Nhân", UI["icon_green"])
    y1 -= 9*mm

    col_w = (content_w - 2*inner) / 2
    label_w = 24*mm
    value_w = col_w - label_w - 2*mm

    _pair(cv, x,           y1,           "Họ tên:",     data["patient_name"],            label_w, value_w, value_bold=True)
    _pair(cv, x,           y1 - row,     "Ngày sinh:",  data.get("dob") or "-",          label_w, value_w)
    _pair(cv, x,           y1 - 2*row,   "SĐT:",        data.get("phone") or "-",        label_w, value_w)

    x2 = x + col_w
    _pair(cv, x2,          y1,           "CCCD:",       data.get("national_id") or "-",  label_w, value_w)
    _pair(cv, x2,          y1 - row,     "Giới tính:",  (data.get("gender") or "-"),     label_w, value_w)

    y = y - card1_h - 7*mm

    # Card exam
    card2_h = 58*mm
    _round_rect(cv, margin, y, content_w, card2_h, 8, UI["exam_bg"], UI["exam_bd"])
    x = margin + inner
    y2 = y - inner
    _section_header(cv, x, y2, "Thông Tin Khám", UI["icon_green"])
    y2 -= 9*mm

    col_w = (content_w - 2*inner) / 2
    label_w = 26*mm
    value_w = col_w - label_w - 2*mm

    _pair(cv, x,           y2,           "Dịch vụ:",    data["service_name"],            label_w, value_w)
    _pair(cv, x,           y2 - row,     "Bác sĩ:",     data["doctor_name"],             label_w, value_w)
    _pair(cv, x,           y2 - 2*row,   "Giá:",        _fmt_vnd(data["cur_price"]),     label_w, value_w,
          value_bold=True, value_color=UI["price"])

    x2 = x + col_w
    _pair(cv, x2,          y2,           "Phòng:",          data["clinic_name"],          label_w, value_w)
    _pair(cv, x2,          y2 - row,     "Số thứ tự:",      str(data.get("queue_number") or "-"), label_w, value_w, value_bold=True)

    # thời gian dự kiến (đo bề rộng label -> value không dính)
    cv.setFont("DejaVu-Bold", 10); cv.setFillColor(UI["title"])
    lbl = "Thời gian khám:"
    cv.drawString(x2, y2 - 2*row, lbl)
    value_x = x2 + max(label_w, cv.stringWidth(lbl, "DejaVu-Bold", 10) + 2*mm)
    cv.setFont("DejaVu-Bold", 10); cv.setFillColor(UI["danger"])
    cv.drawString(value_x, y2 - 2*row, est_str)

    # chip + thời gian thanh toán (cũng đo bề rộng label)
    chip_w, chip_h = 36*mm, 8*mm
    chip_x = x; chip_y_top = y2 - 3*row + 2
    _round_rect(cv, chip_x, chip_y_top, chip_w, chip_h, 3, UI["chip_bg"], UI["chip_bd"])
    cv.setFont("DejaVu-Bold", 9); cv.setFillColor(UI["chip_txt"])
    cv.drawCentredString(chip_x + chip_w/2, chip_y_top - chip_h/2 + 3, "ĐÃ THANH TOÁN")

    cv.setFont("DejaVu-Bold", 10); cv.setFillColor(UI["title"])
    lbl2 = "Thời gian thanh toán:"
    cv.drawString(x2, y2 - 3*row, lbl2)
    value_x2 = x2 + max(label_w, cv.stringWidth(lbl2, "DejaVu-Bold", 10) + 2*mm)
    cv.setFont("DejaVu", 10); cv.setFillColor(UI["title"])
    cv.drawString(value_x2, y2 - 3*row, paid_str)

    y = y - card2_h - 8*mm

    # QR
    qr_payload = f"APPT:{data['id']}|ORDER:{data['order_code']}|PAID_AT:{paid_str}"
    qr_img = _qr_reader(qr_payload)
    qr_size = 48*mm
    cv.drawImage(qr_img, (w - qr_size)/2, y - qr_size, qr_size, qr_size, preserveAspectRatio=True, mask='auto')
    y -= (qr_size + 7*mm)
    cv.setFont("DejaVu", 9); cv.setFillColor(UI["muted"])
    cv.drawCentredString(w/2, y, "Mã QR dùng để check-in tại quầy")
    y -= 10*mm

    # Hint
    hint_h = 28*mm
    _round_rect(cv, margin, y, content_w, hint_h, 6, UI["hint_bg"], UI["hint_bd"])
    cv.setFont("DejaVu-Bold", 10); cv.setFillColor(UI["title"])
    cv.drawString(margin + 9*mm, y - 9, "Hướng dẫn:")
    cv.setFont("DejaVu", 9)
    for t in [
        "Vui lòng mang theo phiếu khám tới quầy/triển khai tự động.",
        "Nếu dùng BHYT, nhớ mang thẻ và giấy tờ liên quan.",
        "Mọi thắc mắc vui lòng liên hệ quầy hướng dẫn.",
    ]:
        y -= 5*mm
        cv.drawString(margin + 12*mm, y, f"• {t}")

    cv.setTitle(f"PhieuKham-{data['id']}")
    cv.showPage(); cv.save()
    pdf_bytes = buf.getvalue(); buf.close()
    return pdf_bytes, f"phieu_kham_{data['id']}.pdf"