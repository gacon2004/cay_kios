from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.doctors.models import DoctorUpdateRequestModel

database = DatabaseConnector()

def create_doctor(user_id: int, full_name: str, specialty: str, phone: str, email: str) -> int:
    result = database.call_procedure("sp_create_doctor", (user_id, full_name, specialty, phone, email))
    return result[0]["doctor_id"]

def get_all_doctors(limit: int = 100, offset: int = 0) -> list[dict]:
    return database.call_procedure("sp_get_all_doctors", (limit, offset))

def get_doctor_by_id(id: int) -> dict:
    result = database.call_procedure("sp_get_doctor_by_id", (id,))
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")
    return result[0]

def update_doctor(id: int, full_name: str = None, specialty: str = None, phone: str = None, email: str = None) -> int:
    result = database.call_procedure("sp_update_doctor", (id, full_name, specialty, phone, email))
    return result[0]["affected_rows"]

def delete_doctor(id: int) -> str:
    result = database.call_procedure("sp_delete_doctor", (id,))
    return result[0]["message"]
