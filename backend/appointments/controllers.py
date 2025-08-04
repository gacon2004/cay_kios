from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.appointments.models import AppointmentCreateModel, AppointmentUpdateModel
from datetime import datetime
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
import base64
import io

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

def create_appointment(patient_id: int, data: AppointmentCreateModel) -> dict:
    queue_sql = """
        SELECT COALESCE(MAX(queue_number), 0) + 1 AS next_queue
        FROM appointments
        WHERE clinic_id = %s AND DATE(appointment_time) = CURDATE()
    """
    queue_result = db.query_get(queue_sql, (data.clinic_id,))
    queue_number = queue_result[0]["next_queue"]

    now = datetime.now()

    # 1. Insert Appointment
    insert_sql = """
        INSERT INTO appointments (
            patient_id, clinic_id, service_id, doctor_id,
            queue_number, appointment_time, printed, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.query_put(
        insert_sql,
        (
            patient_id, data.clinic_id, data.service_id, data.doctor_id,
            queue_number, now, False, "waiting"
        )
    )

    # 2. Get latest appointment by patient (ORDER BY id)
    result = db.query_get(
        """
        SELECT a.*, s.name AS service_name, s.price AS service_price,
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
        "price": appointment["service_price"],
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
        SELECT a.*, s.name AS service_name, s.price AS service_price,
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

def print_appointment_pdf(appointment_id: int, user_id: int) -> StreamingResponse:
    # 1. Lấy thông tin phiếu
    result = db.query_get("""
        SELECT a.*, p.full_name, p.national_id, p.date_of_birth, p.gender, p.phone,
               s.name AS service_name, s.price AS service_price,
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

    # 3. Tạo PDF bằng reportlab
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ==== HEADER ====
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 40, "PHIẾU KHÁM BỆNH")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 60, "Thông tin xác nhận đăng ký khám bệnh")

    # ==== Thông tin bệnh nhân ====
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 100, "🔹 Thông tin bệnh nhân")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 120, f"Họ tên: {a['full_name']}")
    c.drawString(50, height - 140, f"CCCD: {a['national_id']}")
    c.drawString(50, height - 160, f"Ngày sinh: {a['date_of_birth']}")
    c.drawString(50, height - 180, f"Giới tính: {'Nam' if a['gender'] == 'male' else 'Nữ'}")
    c.drawString(50, height - 200, f"Số điện thoại: {a['phone']}")

    # ==== Thông tin khám ====
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, height - 100, "🩺 Thông tin khám bệnh")
    c.setFont("Helvetica", 11)
    c.drawString(310, height - 120, f"Bệnh viện: {a['clinic_name']}")
    c.drawString(310, height - 140, f"Dịch vụ: {a['service_name']} ({a['service_price']}đ)")
    c.drawString(310, height - 160, f"Bác sĩ: {a['doctor_name']}")
    c.drawString(310, height - 180, f"Số thứ tự: {a['queue_number']}")
    c.drawString(310, height - 200, f"Thời gian: {a['appointment_time'].strftime('%H:%M:%S %d/%m/%Y')}")

    # ==== QR Code ====
    if a.get("qr_code"):
        try:
            img_data = base64.b64decode(a["qr_code"])
            img = ImageReader(io.BytesIO(img_data))
            c.drawImage(img, width / 2 - 50, height - 320, width=100, height=100)
        except Exception as e:
            print("Lỗi QR code:", e)

    # ==== Hướng dẫn ====
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 360, "📌 Hướng dẫn:")
    c.drawString(50, height - 380, "• Vui lòng đến đúng giờ hẹn để khám.")
    c.drawString(50, height - 400, "• Mang theo phiếu khám và giấy tờ tùy thân.")
    c.drawString(50, height - 420, "• Gọi tổng đài nếu cần hỗ trợ thêm.")

    c.showPage()
    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=phieu_kham_{appointment_id}.pdf"}
    )