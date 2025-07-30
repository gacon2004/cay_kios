from fastapi import HTTPException, status
from database.connector import DatabaseConnector
from clinics.models import ClinicCreateModel, ClinicUpdateModel

db = DatabaseConnector()

def get_all_clinics() -> list[dict]:
    return db.query_get("SELECT * FROM clinics")

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

def get_clinics_by_service_id(service_id: int) -> list[dict]:
    return db.query_get("""
        SELECT c.* FROM clinics c
        JOIN clinic_service_map m ON c.id = m.clinic_id
        WHERE m.service_id = %s
    """, (service_id,))
