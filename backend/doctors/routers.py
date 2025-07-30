from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from auth.provider import AuthProvider, AuthUser

from doctors.controllers import (
    get_all_doctors,
    get_doctor_by_id,
    update_doctor,
    delete_doctor,
    create_doctor,
)
from doctors.models import (
    DoctorResponseModel,
    DoctorUpdateRequestModel,
    DoctorCreateRequestModel,
)

router = APIRouter()
OAuth2 = HTTPBearer()
auth_handler = AuthProvider()


@router.get("/doctors", response_model=list[DoctorResponseModel])
def get_all_doctors_api():
    doctors = get_all_doctors()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(doctors))


@router.get("/doctors/{doctor_id}", response_model=DoctorResponseModel)
def get_doctor_api(
    doctor_id: int,
    current_user: AuthUser = Depends(auth_handler.get_current_user),
):
    doctor = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(doctor))


@router.post("/doctors", response_model=DoctorResponseModel, status_code=status.HTTP_201_CREATED)
def create_doctor_api(
    doctor_data: DoctorCreateRequestModel,
    current_user: AuthUser = Depends(auth_handler.get_current_user),
):
    new_id = create_doctor(doctor_data)
    created = get_doctor_by_id(new_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(created))


@router.put("/doctors/{doctor_id}", response_model=DoctorResponseModel)
def update_doctor_api(
    doctor_id: int,
    doctor_details: DoctorUpdateRequestModel,
    current_user: AuthUser = Depends(auth_handler.get_current_user),
):
    if doctor_id != doctor_details.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "ID trong URL và payload không khớp"},
        )

    update_doctor(doctor_details)
    updated = get_doctor_by_id(doctor_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(updated))


@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor_api(
    doctor_id: int,
    current_user: AuthUser = Depends(auth_handler.get_current_user),
):
    delete_doctor(doctor_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)