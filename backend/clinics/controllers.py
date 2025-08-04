from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.clinics.models import ClinicCreateModel, ClinicUpdateModel

db = DatabaseConnector()

def get_all_clinics() -> list[dict]:
    return db.query_get("SELECT * FROM clinics",())

def get_clinic_by_id(clinic_id: int) -> dict:
    result = db.query_get("SELECT * FROM clinics WHERE id = %s", (clinic_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy phòng khám")
    return result[0]

def create_clinic(data: ClinicCreateModel) -> dict:
    db.query_put(
        "INSERT INTO clinics (name, location, status) VALUES (%s, %s, %s)",
        (data.name, data.location, data.status)
    )
    result = db.query_get("SELECT * FROM clinics WHERE name = %s ORDER BY id DESC LIMIT 1", (data.name,))
    return result[0]

def update_clinic(clinic_id: int, data: ClinicUpdateModel) -> dict:
    update_fields = []
    values = []
    for k, v in data.dict(exclude_unset=True).items():
        update_fields.append(f"{k} = %s")
        values.append(v)

    if not update_fields:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    values.append(clinic_id)
    sql = f"UPDATE clinics SET {', '.join(update_fields)} WHERE id = %s"
    db.query_put(sql, tuple(values))
    return get_clinic_by_id(clinic_id)

def delete_clinic(clinic_id: int) -> None:
    db.query_put("DELETE FROM clinics WHERE id = %s", (clinic_id,))

def get_clinics_by_service(service_id: int):
    sql = """
        SELECT 
            c.id AS clinic_id,
            c.name AS clinic_name,
            c.status AS clinic_status,
            d.id AS doctor_id,
            d.full_name AS doctor_name,
            d.specialty,
            d.phone
        FROM clinics c
        JOIN clinic_doctor_assignments cda ON c.id = cda.clinic_id
        JOIN doctors d ON cda.doctor_id = d.id
        WHERE c.service_id = %s 
    """
    try:
        rows = db.query_get(sql, (service_id,))
        return rows
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch clinics by service: " + str(e),
        )