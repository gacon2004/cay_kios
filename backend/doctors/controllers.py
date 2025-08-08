from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.doctors.models import DoctorUpdateRequestModel

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
    # 1. Lấy thông tin doctor và user_id
    doctor_result = database.query_get(
        "SELECT id, user_id FROM doctors WHERE id = %s",
        (doctor_id,)
    )

    if not doctor_result:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")

    doctor = doctor_result[0]
    user_id = doctor["user_id"]

    # 2. Xóa clinic_doctor_assignments (nếu có)
    database.query_put(
        "DELETE FROM clinic_doctor_assignments WHERE doctor_id = %s",
        (doctor_id,)
    )

    # 3. Xóa doctor
    database.query_put(
        "DELETE FROM doctors WHERE id = %s",
        (doctor_id,)
    )

    # 4. Xóa user tương ứng
    database.query_put(
        "DELETE FROM users WHERE id = %s",
        (user_id,)
    )