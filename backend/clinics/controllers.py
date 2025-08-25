from typing import List, Optional
from backend.database.connector import DatabaseConnector
from backend.clinics.models import (
    ClinicCreateModel,
    ClinicUpdateModel,
    ClinicResponseModel,
)

db = DatabaseConnector()
# -------------------------------
# Lấy tất cả clinics
# -------------------------------
def get_all_clinics() -> List[ClinicResponseModel]:
    rows = db.call_procedure("sp_get_all_clinics")
    return [ClinicResponseModel(**row) for row in rows]
# -------------------------------
# Lấy clinic theo ID
# -------------------------------
def get_clinic_by_id(clinic_id: int) -> Optional[ClinicResponseModel]:
    rows = db.call_procedure("sp_get_clinic_by_id", [clinic_id])
    if not rows:
        return None
    return ClinicResponseModel(**rows[0])
# -------------------------------
# Lấy clinics theo user (doctor)
# -------------------------------
def get_my_clinics_by_user(user_id: int) -> List[ClinicResponseModel]:
    rows = db.call_procedure("sp_get_my_clinics_by_user", [user_id])
    return [ClinicResponseModel(**row) for row in rows]
# -------------------------------
# Tạo clinic
# -------------------------------
def create_clinic(data: ClinicCreateModel) -> ClinicResponseModel:
    rows = db.call_procedure(
        "sp_create_clinic",
        [data.name, data.location, data.status]
    )
    return ClinicResponseModel(**rows[0])
# -------------------------------
# Update clinic
# -------------------------------
def update_clinic(clinic_id: int, data: ClinicUpdateModel) -> ClinicResponseModel:
    rows = db.call_procedure(
        "sp_update_clinic",
        [clinic_id, data.name, data.location, data.status]
    )
    return ClinicResponseModel(**rows[0])
# -------------------------------
# Delete clinic
# -------------------------------
def delete_clinic(clinic_id: int) -> None:
    db.call_procedure("sp_delete_clinic", [clinic_id])
# -------------------------------
# Lấy clinics theo service
# -------------------------------
def get_clinics_by_service(service_id: int) -> list[dict]:
    rows = db.call_procedure("sp_get_clinics_by_service", [service_id])
    # SP này trả cả clinic + doctor + schedule => tạm giữ dạng dict
    return rows
