
from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.appointments.models import (
    AppointmentCreateModel,
    AppointmentUpdateModel, 
    AppointmentCreateBySlotModel,
    AppointmentCancelResponse
)    
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, white
import io, base64
import qrcode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime, timezone, timedelta
db = DatabaseConnector()


def generate_qr_code(data: dict) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")

def create_appointment(patient_id: int, has_insurances: bool, data: AppointmentCreateModel) -> dict:
    tz_utc7 = timezone(timedelta(hours=7))
    queue_sql = """
        SELECT COALESCE(MAX(queue_number), 0) + 1 AS next_queue
        FROM appointments
        WHERE clinic_id = %s AND DATE(appointment_time) = CURDATE()
    """
    queue_result = db.query_get(queue_sql, (data.clinic_id,))
    queue_number = queue_result[0]["next_queue"]

    now = datetime.now(tz_utc7)
    price_result = db.query_get(
        " SELECT price FROM services WHERE id = %s",
        (data.service_id,)
    )
    price = price_result[0]
    cur_price = price["price"]
    if has_insurances:
        cr_price = cur_price/2
    else:
        cr_price = cur_price
    # 1. Insert Appointment
    insert_sql = """
        INSERT INTO appointments (
            patient_id, clinic_id, service_id, doctor_id,
            queue_number, appointment_time, printed, status, cur_price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.query_put(
        insert_sql,
        (
            patient_id, data.clinic_id, data.service_id, data.doctor_id,
            queue_number, now, False, "waiting", cr_price
        )
    )

    # 2. Get latest appointment by patient (ORDER BY id)
    result = db.query_get(
        """
        SELECT a.*, s.name AS service_name, s.price AS service_price,a.cur_price AS cur_price,
               d.full_name AS doctor_name, c.name AS clinic_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN clinics c ON a.clinic_id = c.id
        WHERE a.patient_id = %s
        ORDER BY a.id DESC LIMIT 1
        """,
        (patient_id,)
    )

    if not result:
        raise HTTPException(status_code=500, detail="Appointment not found after insert")

    appointment = result[0]
    appointment_id = appointment["id"]

    # 3. Get Patient Info
    patient_result = db.query_get("SELECT full_name FROM patients WHERE id = %s", (patient_id,))
    if not patient_result:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = patient_result[0]

    # 4. Generate QR Code
    qr_payload = {
        "appointment_id": appointment_id,
        "patient_name": patient["full_name"],
        "service_name": appointment["service_name"],
        "price": appointment["cur_price"],
        "queue_number": queue_number,
        "created_at": now.isoformat()
    }
    qr_code_base64 = generate_qr_code(qr_payload)

    # 5. Update QR code into appointment
    db.query_put(
        "UPDATE appointments SET qr_code = %s WHERE id = %s",
        (qr_code_base64, appointment_id)
    )

    appointment["qr_code"] = qr_code_base64
    return appointment

def get_my_appointments(patient_id: int) -> list[dict]:
    sql = """
        SELECT a.*, s.name AS service_name, a.cur_price AS service_price,
               d.full_name AS doctor_name, c.name AS clinic_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN clinics c ON a.clinic_id = c.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_time DESC
    """
    return db.query_get(sql, (patient_id,))

def update_appointment(appointment_id: int, data: AppointmentUpdateModel) -> dict:
    fields = []
    values = []

    for field, value in data.dict(exclude_unset=True).items():
        fields.append(f"{field} = %s")
        values.append(value)

    if not fields:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    values.append(appointment_id)

    sql = f"""
        UPDATE appointments SET {', '.join(fields)}
        WHERE id = %s
    """
    db.query_put(sql, tuple(values))
    return {"message": "Cập nhật thành công"}

def delete_appointment(appointment_id: int) -> dict:
    sql = "DELETE FROM appointments WHERE id = %s"
    db.query_put(sql, (appointment_id,))
    return {"message": "Xóa thành công"}

# Đăng ký font Unicode
pdfmetrics.registerFont(TTFont("DejaVu", "backend/fonts/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "backend/fonts/DejaVuSans-Bold.ttf"))

def print_appointment_pdf(appointment_id: int, has_insurances: bool, user_id: int) -> StreamingResponse:
    # 1. Lấy thông tin phiếu
    result = db.query_get("""
        SELECT a.*, p.full_name, p.national_id, p.date_of_birth, p.gender, p.phone,
               s.name AS service_name, a.cur_price AS service_price,
               d.full_name AS doctor_name, c.name AS clinic_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN services s ON a.service_id = s.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN clinics c ON a.clinic_id = c.id
        WHERE a.id = %s
    """, (appointment_id,))

    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu khám")

    a = result[0]

    # 2. Kiểm tra quyền bệnh nhân
    if a["patient_id"] != user_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền in phiếu khám này")


    formatted_price = f"{a['service_price']:,.0f} VNĐ"
    # 3. Tạo PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ==== Header ====
    c.setFillColor(HexColor("#111827"))
    c.setFont("DejaVu-Bold", 20)
    c.drawCentredString(width / 2, height - 50, "Hoàn Thành Đăng Ký")

    c.setFont("DejaVu", 12)
    c.setFillColor(HexColor("#6B7280"))
    c.drawCentredString(width / 2, height - 70, "Kiểm tra thông tin và in phiếu khám")

    # ==== Box Thông Tin Bệnh Nhân ====
    left_x = 50
    top_y = height - 120
    box_w = 240
    box_h = 160

    c.setFillColor(HexColor("#E0ECFF"))
    c.roundRect(left_x, top_y - box_h, box_w, box_h, 10, fill=1, stroke=0)

    c.setFont("DejaVu-Bold", 12)
    c.setFillColor(HexColor("#1D4ED8"))
    c.drawString(left_x + 10, top_y - 20, "Thông Tin Bệnh Nhân")

    c.setFont("DejaVu", 10)
    c.setFillColor(HexColor("#111827"))
    c.drawString(left_x + 10, top_y - 40, f"Họ tên: {a['full_name']}")
    c.drawString(left_x + 10, top_y - 58, f"CCCD: {a['national_id']}")
    c.drawString(left_x + 10, top_y - 76, f"Ngày sinh: {a['date_of_birth']}")
    c.drawString(left_x + 10, top_y - 94, f"Giới tính: {'Nam' if a['gender'] == 'male' else 'Nữ'}")
    c.drawString(left_x + 10, top_y - 112, f"SDT: {a['phone']}")

    # ==== Box Thông Tin Khám ====
    right_x = width - left_x - box_w
    c.setFillColor(HexColor("#D1FAE5"))
    c.roundRect(right_x, top_y - box_h, box_w, box_h, 10, fill=1, stroke=0)

    c.setFont("DejaVu-Bold", 12)
    c.setFillColor(HexColor("#059669"))
    c.drawString(right_x + 10, top_y - 20, "Thông Tin Khám")

    c.setFont("DejaVu", 10)
    c.setFillColor(HexColor("#111827"))
    c.drawString(right_x + 10, top_y - 40, f"Dịch vụ: {a['service_name']}")
    c.drawString(right_x + 10, top_y - 58, f"Phòng: {a['clinic_name']}")
    c.drawString(right_x + 10, top_y - 76, f"Bác sĩ: {a['doctor_name']}")
    c.drawString(right_x + 10, top_y - 94, f"Số thứ tự: {a['queue_number']}")
    c.drawString(right_x + 10, top_y - 112, f"Giá tiền: {formatted_price}")
    c.drawString(right_x + 10, top_y - 130, f"Thời gian: {a['appointment_time'].strftime('%H:%M:%S %d/%m/%Y')}")

    # ==== QR Code ====
    if a.get("qr_code"):
        try:
            img_data = base64.b64decode(a["qr_code"])
            img = ImageReader(io.BytesIO(img_data))
            c.drawImage(img, width / 2 - 50, top_y - box_h - 120, width=100, height=100)
        except Exception as e:
            print("Lỗi QR code:", e)

    # ==== Hướng dẫn ====
    guide_top = top_y - box_h - 160
    c.setFillColor(HexColor("#FEF3C7"))
    c.roundRect(40, guide_top - 70, width - 80, 60, 10, fill=1, stroke=0)

    c.setFillColor(HexColor("#92400E"))
    c.setFont("DejaVu-Bold", 11)
    c.drawString(50, guide_top - 15, "Hướng dẫn:")

    c.setFont("DejaVu", 9)
    c.drawString(60, guide_top - 30, "• Vui lòng đến phòng khám đúng giờ hẹn")
    c.drawString(60, guide_top - 45, "• Mang theo phiếu khám và giấy tờ tùy thân")
    c.drawString(60, guide_top - 60, "• Liên hệ tổng đài nếu cần hỗ trợ")

    # ==== Kết thúc ====
    c.showPage()
    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=phieu_kham_{appointment_id}.pdf"}
    )

def create_appointment_by_slot(patient_id: int, data: AppointmentCreateBySlotModel) -> dict:
    """
    Đặt lịch theo slot_start (gọi SP sp_book_appointment) rồi SELECT lại chi tiết
    để trả về đúng AppointmentResponseModel.
    """
    try:
        sets = db.call_proc("sp_book_appointment", (
            patient_id, data.clinic_id, data.service_id,
            data.doctor_id, data.slot_start, data.price
        ))
        if not sets or not sets[0]:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Không tạo được lịch")

        new_id = sets[0][0]["id"]

        # SELECT lại chi tiết để trả đúng AppointmentResponseModel
        row = db.query_get("""
            SELECT a.*, 
                   s.name  AS service_name, 
                   s.price AS service_price,
                   a.cur_price AS cur_price,
                   d.full_name AS doctor_name, 
                   c.name AS clinic_name
            FROM appointments a
            JOIN services s ON a.service_id = s.id
            JOIN doctors  d ON a.doctor_id = d.id
            JOIN clinics  c ON a.clinic_id = c.id
            WHERE a.id = %s
            LIMIT 1
        """, (new_id,))
        if not row:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Không đọc được chi tiết lịch vừa tạo")

        return row[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Đặt lịch thất bại: {e}")

def cancel_appointment_by_patient(appointment_id: int, patient_id: int) -> dict:
    """
    Bệnh nhân hủy lịch của chính mình (gọi SP sp_cancel_appointment_by_patient).
    """
    try:
        sets = db.call_proc("sp_cancel_appointment_by_patient", (appointment_id, patient_id))
        affected = (sets[0][0]["affected"] if sets and sets[0] else 0)
        if affected == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Không thể hủy (không thuộc bạn hoặc trạng thái không cho phép)")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Hủy lịch thất bại: {e}")