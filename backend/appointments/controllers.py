from fastapi import HTTPException, status
from database.connector import DatabaseConnector
from appointments.models import AppointmentCreateModel
from datetime import datetime
import qrcode
import base64
from io import BytesIO

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
