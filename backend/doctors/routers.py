from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from backend.auth.providers.auth_providers import AuthProvider, DoctorUser
from typing import List

from backend.doctors.controllers import (
    get_all_doctors,
    get_doctor_by_id,
    update_doctor,
    delete_doctor,
)
from backend.doctors.models import (
    DoctorResponseModel,
    DoctorUpdateRequestModel,
)

router = APIRouter()
OAuth2 = HTTPBearer()
auth_handler = AuthProvider()

router = APIRouter(prefix="/doctors", tags=["Doctors"])


# API: Lấy danh sách tất cả bác sĩ (chỉ admin)
@router.get("/", response_model=List[DoctorResponseModel])
async def get_all_doctors_api(
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user)
):
    doctors = get_all_doctors()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(doctors)
    )


# API: Lấy thông tin hồ sơ của chính bác sĩ đang đăng nhập
@router.get("/me", response_model=DoctorResponseModel)
async def get_my_doctor_profile(
    current_user: dict = Depends(auth_handler.get_current_doctor_user)
):
    doctor_id = current_user["id"]
    doctor = get_doctor_by_id(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")

    return doctor


# API: Cập nhật hồ sơ của chính bác sĩ đang đăng nhập
@router.put("/me", response_model=DoctorResponseModel)
async def update_my_doctor_profile(
    update_data: DoctorUpdateRequestModel,
    current_user: dict = Depends(auth_handler.get_current_doctor_user)
):
    doctor_id = current_user["id"]

    # Bảo đảm user chỉ update chính mình
    if update_data.id != doctor_id:
        raise HTTPException(
            status_code=400,
            detail="ID trong payload không khớp với tài khoản đăng nhập"
        )

    # Truyền đúng từng field thay vì truyền nguyên object
    update_doctor(
        id=update_data.id,
        full_name=update_data.full_name,
        specialty=update_data.specialty,
        phone=update_data.phone,
        email=update_data.email
    )

    updated = get_doctor_by_id(doctor_id)
    return updated


# API: Lấy thông tin chi tiết 1 bác sĩ (chỉ admin)
@router.get("/{doctor_id}", response_model=DoctorResponseModel)
async def get_doctor_api(
    doctor_id: int,
    current_user: dict = Depends(auth_handler.get_current_admin_user),
):
    doctor = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(doctor))


# API: Cập nhật thông tin 1 bác sĩ theo ID (chỉ admin)
@router.put("/{doctor_id}", response_model=DoctorResponseModel)
def update_doctor_api(
    doctor_id: int,
    doctor_details: DoctorUpdateRequestModel,
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user),
):
    if doctor_id != doctor_details.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "ID trong URL và payload không khớp"},
        )

    # ✅ Truyền đúng từng field
    update_doctor(
        id=doctor_details.id,
        full_name=doctor_details.full_name,
        specialty=doctor_details.specialty,
        phone=doctor_details.phone,
        email=doctor_details.email
    )

    updated = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(updated))


# API: Xóa 1 bác sĩ theo ID (chỉ admin)
@router.delete("/{doctor_id}", status_code=status.HTTP_200_OK)
def delete_doctor_api(
    doctor_id: int,
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user),
):
    delete_doctor(doctor_id)
    return {"message": "Xóa bác sĩ thành công"}
