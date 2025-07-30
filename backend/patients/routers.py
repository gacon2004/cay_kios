from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from backend.auth.provider import AuthProvider, AuthUser
from backend.patients.models import PatientUpdateRequestModel

from backend.patients.controllers import (
    update_patient,
    get_all_patients,
    get_patient_by_id,
    get_patient_profile,
    get_patients_by_national_id
)
from backend.patients.models import (
    PatientUpdateRequestModel,
    PatientResponseModel,
)

router = APIRouter()
OAuth2 = HTTPBearer()
auth_handler = AuthProvider()

@router.get("/patients/me", response_model=PatientResponseModel)
def get_me(current_user: AuthUser = Depends(auth_handler.get_current_patient_user)):
    return get_patient_profile(current_user)

@router.get("/patients", response_model=list[PatientResponseModel])
def get_all_patients_api(
    # current_user: AuthUser = Depends(auth_handler.get_current_user),
):
    """
    Lấy danh sách tất cả bệnh nhân.
    """
    patients = get_all_patients()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(patients))


@router.get("/patients/{patient_id}", response_model=PatientResponseModel)
def get_patient_api(
    patient_id: int,
    current_user: AuthUser = Depends(auth_handler.get_current_patient_user),
):
    """
    Lấy thông tin chi tiết của một bệnh nhân theo ID.
    """
    patient = get_patient_by_id(patient_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(patient))


@router.put("/patients/{patient_id}", response_model=PatientResponseModel)
def update_patient_api(
    patient_id: int,
    patient_details: PatientUpdateRequestModel,
    current_user: AuthUser = Depends(auth_handler.get_current_patient_user),
):
    """
    Cập nhật thông tin bệnh nhân theo ID.
    """
    if patient_id != patient_details.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "ID trong URL và trong payload không khớp"},
        )

    update_patient(patient_details)
    updated = get_patient_by_id(patient_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(updated))
