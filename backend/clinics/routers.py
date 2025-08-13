from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from fastapi.encoders import jsonable_encoder
from backend.auth.providers.auth_providers import AuthProvider, AdminUser, DoctorUser
from backend.clinics.models import (
    ClinicCreateModel,
    ClinicUpdateModel,
    ClinicResponseModel,
)
from backend.clinics.controllers import (
    get_all_clinics,
    get_clinic_by_id,
    create_clinic,
    update_clinic,
    delete_clinic,
    get_clinics_by_service,
    get_my_clinics_by_user,
)

auth_handler= AuthProvider()

router = APIRouter(prefix="/clinics", tags=["Clinics"])


@router.get("/", response_model=list[ClinicResponseModel])
def list_clinics():
    return jsonable_encoder(get_all_clinics())


@router.get("/{clinic_id}", response_model=ClinicResponseModel)
def get_clinic(clinic_id: int):
    return jsonable_encoder(get_clinic_by_id(clinic_id))

@router.get("/doctor/me", response_model=List[ClinicResponseModel])
def get_my_clinics(current_user = Depends(auth_handler.get_current_doctor_user)):
    # Token chắc chắn có user_id
    if isinstance(current_user, dict):
        user_id = current_user.get("user_id", current_user.get("id"))
    else:
        user_id = getattr(current_user, "user_id", getattr(current_user, "id", None))

    if not user_id:
        raise HTTPException(status_code=401, detail="Token thiếu user_id")

    data = get_my_clinics_by_user(int(user_id))
    return jsonable_encoder(data)

@router.post("/", response_model=ClinicResponseModel, status_code=status.HTTP_201_CREATED)
def create_new_clinic(
    data: ClinicCreateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    return jsonable_encoder(create_clinic(data))


@router.put("/{clinic_id}", response_model=ClinicResponseModel)
def update_existing_clinic(
    clinic_id: int,
    data: ClinicUpdateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    return jsonable_encoder(update_clinic(clinic_id, data))


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_clinic(
    clinic_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    delete_clinic(clinic_id)
    return JSONResponse(status_code=204, content={})


@router.get("/by-service/{service_id}")
def api_clinics_by_service(service_id: int):
    data = get_clinics_by_service(service_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))