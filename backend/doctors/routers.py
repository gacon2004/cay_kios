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

@router.get("/", response_model=List[DoctorResponseModel])
async def get_all_doctors_api(
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user)
):
    doctors = get_all_doctors()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(doctors)
    )

@router.get("/me", response_model=DoctorResponseModel)
async def get_my_doctor_profile(
    current_user: dict = Depends(auth_handler.get_current_doctor_user)
):
    doctor_id = current_user["id"]
    doctor = get_doctor_by_id(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")
    
    return doctor

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

    update_doctor(update_data)
    updated = get_doctor_by_id(doctor_id)
    return updated

@router.get("/{doctor_id}", response_model=DoctorResponseModel)
async def get_doctor_api(
    doctor_id: int,
    current_user: dict = Depends(auth_handler.get_current_admin_user),
):
    doctor = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(doctor))

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

    update_doctor(doctor_details)
    updated = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(updated))


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor_api(
    doctor_id: int,
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user),
):
    delete_doctor(doctor_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)