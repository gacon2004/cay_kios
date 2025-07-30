from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.services.models import ServiceCreateModel, ServiceUpdateModel

db = DatabaseConnector()

def get_all_services() -> list[dict]:
    return db.query_get("SELECT * FROM services", ())

def get_service_by_id(service_id: int) -> dict:
    result = db.query_get("SELECT * FROM services WHERE id = %s", (service_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return result[0]

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

def get_services_with_clinics_doctors() -> list[dict]:
    db = DatabaseConnector()

    sql = """
        SELECT 
            s.id AS service_id, s.name AS service_name, s.description, s.price,
            c.id AS clinic_id, c.name AS clinic_name, c.status,
            d.id AS doctor_id, d.full_name AS doctor_name
        FROM services s
        LEFT JOIN clinics c ON s.id = c.service_id
        LEFT JOIN doctors d ON d.id = c.doctor_id
        ORDER BY s.id, c.id
        """
    rows = db.query_get(sql, ())

    services = {}
    for row in rows:
        sid = row["service_id"]
        if sid not in services:
            services[sid] = {
                "id": sid,
                "name": row["service_name"],
                "description": row["description"],
                "price": row["price"],
                "clinics": []
            }

        if row["clinic_id"]:
            clinic = {
                "id": row["clinic_id"],
                "name": row["clinic_name"],
                "location": row["location"],
                "status": row["status"],
                "doctor": {
                    "id": row["doctor_id"],
                    "full_name": row["doctor_name"],
                    "specialty": row["specialty"]
                } if row["doctor_id"] else None
            }

            # tránh trùng phòng khám nếu nhiều bác sĩ
            if clinic not in services[sid]["clinics"]:
                services[sid]["clinics"].append(clinic)

    return list(services.values())