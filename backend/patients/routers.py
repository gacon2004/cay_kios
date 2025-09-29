from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse

from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from backend.auth.providers.auth_providers import AuthProvider, AdminUser
from backend.patients.models import (
    PatientUpdateRequestModel,
    PatientResponseModel,
)
from backend.patients.controllers import (
    get_patient_profile,
    update_patient,
    get_all_patients,
    get_patient_by_id,
    delete_patient_by_id,
)

router = APIRouter(prefix="/patients", tags=["Patients"])
OAuth2 = HTTPBearer()
auth_admin_handler = AuthProvider()
auth_patient_handler = PatientProvider()


# Lấy hồ sơ bệnh nhân đang đăng nhập
@router.get("/me", response_model=PatientResponseModel)
def get_me(current_user: AuthUser = Depends(auth_patient_handler.get_current_patient_user)):
    patient = get_patient_profile(current_user)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(patient)
    )


# Cập nhật hồ sơ bệnh nhân đang đăng nhập
@router.put("/me", response_model=PatientResponseModel)
def update_me_api(
    data: PatientUpdateRequestModel,
    current_user: AuthUser = Depends(auth_patient_handler.get_current_patient_user)
):
    patient_id = current_user["id"]
    update_patient(patient_id, data)
    updated = get_patient_by_id(patient_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(updated)
    )

# Admin: Lấy danh sách bệnh nhân
@router.get("/")
def get_all_patients_api(
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user),
    limit: int = Query(..., description="Số bản ghi mỗi trang"),
    offset: int = Query(..., description="Bản ghi bắt đầu"),
    search: str = Query("", description="Từ khóa tìm kiếm (tên, CCCD, SDT, ...)")
):
    result = get_all_patients(limit, offset, search)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result)
    )

# Admin: Lấy chi tiết bệnh nhân theo ID
@router.get("/{patient_id}", response_model=PatientResponseModel)
def get_patient_api(
    patient_id: int,
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user),
):
    patient = get_patient_by_id(patient_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(patient)
    )
# Admin: Cập nhật thông tin bệnh nhân theo ID
@router.put("/{patient_id}", response_model=PatientResponseModel)
def update_patient_api(
    patient_id: int,
    patient_details: PatientUpdateRequestModel,
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user),
):
    if patient_id != patient_details.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "ID trong URL và trong payload không khớp"},
        )
    update_patient(patient_id, patient_details)
    updated = get_patient_by_id(patient_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(updated)
    )


# Admin: Xóa bệnh nhân
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_api(
    patient_id: int,
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user),
):
    delete_patient_by_id(patient_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
