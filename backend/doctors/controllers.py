from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.doctors.models import DoctorUpdateRequestModel, DoctorCreateRequestModel

database = DatabaseConnector()

def get_all_doctors(limit: int = 100, offset: int = 0) -> list[dict]:
    sql = """
        SELECT id, full_name, specialty, phone, email, created_at
        FROM doctors
        LIMIT %s OFFSET %s
    """
    return database.query_get(sql, (limit, offset))

def get_doctor_by_id(id: int) -> dict:
    sql = """
        SELECT id, full_name, specialty, phone, email, created_at
        FROM doctors
        WHERE id = %s
    """
    result = database.query_get(sql, (id,))
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")
    return result[0]

def create_doctor(doctor_model: DoctorCreateRequestModel) -> int:
    sql = """
        INSERT INTO doctors (full_name, specialty, phone, email)
        VALUES (%s, %s, %s, %s)
    """
    params = (
        doctor_model.full_name,
        doctor_model.specialty,
        doctor_model.phone,
        doctor_model.email,
    )
    return database.query_post(sql, params)

def update_doctor(doctor_model: DoctorUpdateRequestModel) -> int:
    update_fields = []
    params = []

    for field, value in doctor_model.dict(exclude={"id"}).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if not update_fields:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    params.append(doctor_model.id)

    sql = f"""
        UPDATE doctors
        SET {', '.join(update_fields)}
        WHERE id = %s
    """
    return database.query_put(sql, tuple(params))

def delete_doctor(doctor_id: int) -> None:
    sql = "DELETE FROM doctors WHERE id = %s"
    affected = database.query_put(sql, (doctor_id,))
    if affected == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")