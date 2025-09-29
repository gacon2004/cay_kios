from typing import Optional
from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from backend.patients.models import PatientUpdateRequestModel

auth_handler = PatientProvider()
database = DatabaseConnector()

# Hàm gọi Stored Procedure
def call_procedure(proc_name: str, params: tuple = ()) -> list[dict]:
    return database.call_procedure(proc_name, params)


# Lấy hồ sơ bệnh nhân hiện tại
def get_patient_profile(current_user: AuthUser) -> dict:
    result = call_procedure("sp_get_patient_by_id", (current_user["id"],))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bệnh nhân"
        )
    return result[0]

# Cập nhật thông tin bệnh nhân
def update_patient(patient_id: int, patient_model: PatientUpdateRequestModel) -> int:
    # Check CCCD/CMND trùng lặp
    existing = call_procedure("sp_get_patient_by_national_id", (patient_model.national_id,))
    if len(existing) > 0 and existing[0]["id"] != patient_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CMND/CCCD đã tồn tại trong hệ thống",
        )

    params = (
        patient_id,
        patient_model.national_id,
        patient_model.full_name,
        patient_model.date_of_birth,
        patient_model.gender,
        patient_model.phone,
        patient_model.ward,
        patient_model.district,
        patient_model.province,
        patient_model.occupation,
        patient_model.ethnicity,
    )

    call_procedure("sp_update_patient", params)
    return 1  # Có thể đổi thành rowcount nếu procedure trả về


# Lấy danh sách bệnh nhân với phân trang + tìm kiếm
def get_all_patients(limit: int, offset: int, search: str = "") -> dict:
    # Gọi procedure với search
    result = database.call_procedure("sp_get_all_patients", (limit, offset, search))

    if not result:
        return {
            "data": [],
            "pagination": {
                "page": (offset // limit) + 1 if limit else 1,
                "limit": limit,
                "totalRecords": 0,
                "totalPages": 0
            }
        }

    # Lấy meta từ record đầu tiên
    meta = {
        "totalRecords": result[0]["totalRecords"],
        "totalPages": result[0]["totalPages"]
    }

    # Xóa totalRecords & totalPages khỏi từng row để tránh lặp
    for row in result:
        row.pop("totalRecords", None)
        row.pop("totalPages", None)

    return {
        "data": result,
        "pagination": {
            "page": (offset // limit) + 1,
            "limit": limit,
            **meta
        }
    }


# Tìm bệnh nhân theo CCCD/CMND
def get_patients_by_national_id(national_id: str) -> list[dict]:
    return call_procedure("sp_get_patient_by_national_id", (national_id,))


# Lấy bệnh nhân theo ID
def get_patient_by_id(patient_id: int) -> dict:
    result = call_procedure("sp_get_patient_by_id", (patient_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bệnh nhân"
        )
    return result[0]


# Xóa bệnh nhân theo ID
def delete_patient_by_id(patient_id: int) -> None:
    call_procedure("sp_delete_patient", (patient_id,))
