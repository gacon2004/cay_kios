from fastapi import HTTPException, status
from typing import List, Dict, Any
from backend.database.connector import DatabaseConnector
from backend.services.models import ServiceCreateModel, ServiceUpdateModel

db = DatabaseConnector()

def get_all_services(has_insurances: bool = False) -> list[dict]:
    services = db.query_get("SELECT * FROM services", ())
    
    if has_insurances:
        for s in services:
            if s.get("price") is not None:
                s["price"] = s["price"] / 2  
    return services

def get_service_by_id(service_id: int) -> dict:
    result = db.query_get("SELECT * FROM services WHERE id = %s", (service_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return result[0]

def get_my_services_by_user(user_id: int) -> List[Dict[str, Any]]:
    """
    Trả về các dịch vụ (services) mà bác sĩ thuộc về,
    dựa vào doctors.user_id -> clinic_doctor_assignments -> clinics -> services
    """
    sql = """
        SELECT DISTINCT
            s.id,
            s.name,
            s.status,
            s.description
        FROM doctors d
        JOIN clinic_doctor_assignments cda ON cda.doctor_id = d.id
        JOIN clinics c ON c.id = cda.clinic_id
        JOIN services s ON s.id = c.service_id
        WHERE d.user_id = %s
        ORDER BY s.id
    """
    return db.query_get(sql, (user_id,))

def create_service(data: ServiceCreateModel) -> int:
    return db.query_put(
        "INSERT INTO services (name, description, price) VALUES (%s, %s, %s)",
        (data.name, data.description, data.price)
    )

def update_service(data: ServiceUpdateModel) -> int:
    update_fields = []
    params = []

    for field, value in data.dict(exclude={"id"}).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if not update_fields:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    params.append(data.id)
    sql = f"UPDATE services SET {', '.join(update_fields)} WHERE id = %s"
    return db.query_put(sql, tuple(params))

def delete_service(service_id: int) -> int:
    return db.query_put("DELETE FROM services WHERE id = %s", (service_id,))
