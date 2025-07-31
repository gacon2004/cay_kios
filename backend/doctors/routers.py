from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from backend.auth.providers.auth_providers import AuthProvider, DoctorUser

from backend.doctors.controllers import (
    get_all_doctors,
    get_doctor_by_id,
    update_doctor,
    delete_doctor,
    create_doctor,
)
from backend.doctors.models import (
    DoctorResponseModel,
    DoctorUpdateRequestModel,
    DoctorCreateRequestModel,
)

router = APIRouter()
OAuth2 = HTTPBearer()
auth_handler = AuthProvider()

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/", response_model=list[DoctorResponseModel])
def get_all_doctors_api():
    doctors = get_all_doctors()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(doctors))


@router.get("/{doctor_id}", response_model=DoctorResponseModel)
async def get_doctor_api(
    doctor_id: int,
    current_user: dict = Depends(auth_handler.get_current_admin_user),
):
    doctor = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(doctor))


@router.post("/", response_model=DoctorResponseModel, status_code=status.HTTP_201_CREATED)
def create_doctor_api(
    doctor_data: DoctorCreateRequestModel,
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user),
):
    new_id = create_doctor(doctor_data)
    created = get_doctor_by_id(new_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(created))


@router.put("/{doctor_id}", response_model=DoctorResponseModel)
def update_doctor_api(
    doctor_id: int,
    doctor_details: DoctorUpdateRequestModel,
    current_user: dict = Depends(auth_handler.get_current_admin_or_doctor_user),
):
    if current_user["role"] == "doctor" and current_user["id"] != doctor_id:
        raise HTTPException(
            status_code=403,
            detail="Không được sửa thông tin bác sĩ khác"
        )

    if doctor_id != doctor_details.id:
        raise HTTPException(
            status_code=400,
            detail="ID trong URL và payload không khớp"
        )

    update_doctor(doctor_details)
    updated = get_doctor_by_id(doctor_id)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(updated)
    )


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor_api(
    doctor_id: int,
    current_user: DoctorUser = Depends(auth_handler.get_current_admin_user),
):
    delete_doctor(doctor_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)