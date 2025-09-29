from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
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

auth_handler = AuthProvider()
router = APIRouter(prefix="/clinics", tags=["Clinics"])



# GET: Lấy tất cả clinics

@router.get("/", response_model=List[ClinicResponseModel])
def list_clinics():
    return get_all_clinics()



# GET: Lấy clinic theo ID

@router.get("/{clinic_id}", response_model=ClinicResponseModel)
def get_clinic(clinic_id: int):
    clinic = get_clinic_by_id(clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic



# GET: Lấy clinics theo doctor (user hiện tại)
@router.get("/doctor/me", response_model=List[ClinicResponseModel])
def get_my_clinics(current_user: dict = Depends(auth_handler.get_current_doctor_user)):
    if not current_user.get("id"):
        raise HTTPException(status_code=401, detail="Token thiếu user_id")
    return get_my_clinics_by_user(current_user["id"])

# POST: Tạo clinic mới
@router.post("/", response_model=ClinicResponseModel, status_code=status.HTTP_201_CREATED)
def create_new_clinic(
    data: ClinicCreateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    return create_clinic(data)



# PUT: Update clinic

@router.put("/{clinic_id}", response_model=ClinicResponseModel)
def update_existing_clinic(
    clinic_id: int,
    data: ClinicUpdateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    return update_clinic(clinic_id, data)



# DELETE: Xoá clinic

@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_clinic(
    clinic_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    delete_clinic(clinic_id)
    return



# GET: Lấy clinics theo service

@router.get("/by-service/{service_id}")
def api_clinics_by_service(service_id: int):
    return get_clinics_by_service(service_id)
