from fastapi import HTTPException, status
from typing import List, Dict, Any, Tuple
from backend.database.connector import DatabaseConnector
from backend.clinics.models import ClinicCreateModel, ClinicUpdateModel

db = DatabaseConnector()

def get_all_clinics() -> list[dict]:

    return db.query_get("SELECT * FROM clinics", ())


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

def get_clinics_by_service(service_id: int) -> List[Dict[str, Any]]:
    sql = """
        SELECT
            c.id   AS clinic_id,
            c.name AS clinic_name,
            c.status AS clinic_status,

            d.id        AS doctor_id,
            d.full_name AS doctor_name,
            d.specialty AS specialty,
            d.phone     AS phone,

            ds.id AS schedule_id,
            TIME_FORMAT(ds.start_time, '%%H:%%i') AS start_time,
            TIME_FORMAT(ds.end_time,   '%%H:%%i') AS end_time,
            ds.max_patients,
            COALESCE(ds.booked_patients, 0) AS booked_patients,
            CASE
              WHEN ds.id IS NULL THEN NULL
              ELSE GREATEST(ds.max_patients - COALESCE(ds.booked_patients, 0), 0)
            END AS remaining
        FROM clinics c
        JOIN clinic_doctor_assignments cda 
               ON c.id = cda.clinic_id
        JOIN doctors d 
               ON cda.doctor_id = d.id
        LEFT JOIN doctor_schedules ds
               ON ds.clinic_id = c.id
              AND ds.doctor_id = d.id
              AND DATE(ds.work_date) = CURDATE()   -- so sánh bỏ giờ
              AND ds.status = 1
        WHERE c.service_id = %s
        ORDER BY c.id, d.id, (ds.start_time IS NULL), ds.start_time
    """
    try:
        rows = db.query_get(sql, (service_id,))
        result: List[Dict[str, Any]] = []
        index: Dict[Tuple[int, int], int] = {}

        for r in rows:
            clinic_id = r.get("clinic_id")
            doctor_id = r.get("doctor_id")
            if clinic_id is None or doctor_id is None:
                continue

            key = (clinic_id, doctor_id)
            if key not in index:
                index[key] = len(result)
                result.append({
                    "clinic_id": clinic_id,
                    "clinic_name": r.get("clinic_name") or "",
                    "clinic_status": r.get("clinic_status"),
                    "doctor_id": doctor_id,
                    "doctor_name": r.get("doctor_name") or "",
                    "specialty": r.get("specialty") or "",
                    "phone": r.get("phone") or "",
                    "shifts": []
                })

            if r.get("schedule_id") is not None:
                remaining = r.get("remaining")
                result[index[key]]["shifts"].append({
                    "schedule_id": r.get("schedule_id"),
                    "start_time": r.get("start_time") or "",
                    "end_time":   r.get("end_time") or "",
                    "max_patients": r.get("max_patients") or 0,
                    "booked_patients": r.get("booked_patients") or 0,
                    "remaining": int(remaining) if remaining is not None else 0,
                    "is_full": (remaining is not None and int(remaining) <= 0),
                })

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL/Python error: {e!r}"
        )