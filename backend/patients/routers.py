from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from backend.patients.models import PatientUpdateRequestModel
from backend.auth.providers.auth_providers import AuthProvider, AdminUser
from backend.auth.providers.partient_provider import PatientProvider
from backend.patients.controllers import (
    update_patient,
    get_all_patients,
    get_patient_by_id,
    get_patient_profile,
    delete_patient_by_id,
)
from backend.patients.models import (
    PatientUpdateRequestModel,
    PatientResponseModel,
)

router = APIRouter()
OAuth2 = HTTPBearer()
auth_admin_handler = AuthProvider()
auth_patient_handler = PatientProvider()

<<<<<<< HEAD
@router.get("/patients/me", response_model=PatientResponseModel)
def get_me(current_user: AuthUser = Depends(auth_handler.get_current_patient_user)):
=======
router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/me", response_model=PatientResponseModel)
def get_me(current_user: AuthUser = Depends(auth_patient_handler.get_current_patient_user)):
>>>>>>> 86e17ff2518c06ad2e91c23614cd316727d519ac
    return get_patient_profile(current_user)

@router.put("/me", response_model=PatientResponseModel)
def update_me_api(
    data: PatientUpdateRequestModel,
    current_user: dict = Depends(auth_patient_handler.get_current_patient_user)
):
    """
    Cập nhật thông tin của chính bệnh nhân đang đăng nhập.
    """
    patient_id = current_user["id"]
    
    update_patient(patient_id, data)
    updated = get_patient_by_id(patient_id)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(updated)
    )

@router.get("/", response_model=list[PatientResponseModel])
def get_all_patients_api(
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user)
):
    """
    Lấy danh sách tất cả bệnh nhân (chỉ dành cho admin).
    """
    patients = get_all_patients()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(patients)
    )

@router.get("/{patient_id}", response_model=PatientResponseModel)
def get_patient_api(
    patient_id: int,
<<<<<<< HEAD
    current_user: AuthUser = Depends(auth_handler.get_current_patient_user),
=======
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user),
>>>>>>> 86e17ff2518c06ad2e91c23614cd316727d519ac
):
    """
    Lấy thông tin chi tiết của một bệnh nhân theo ID.
    """
    patient = get_patient_by_id(patient_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(patient))


@router.put("/{patient_id}", response_model=PatientResponseModel)
def update_patient_api(
    patient_id: int,
    patient_details: PatientUpdateRequestModel,
<<<<<<< HEAD
    current_user: AuthUser = Depends(auth_handler.get_current_patient_user),
=======
    current_user: AdminUser = Depends(auth_patient_handler.get_current_patient_user),
>>>>>>> 86e17ff2518c06ad2e91c23614cd316727d519ac
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

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_api(
    patient_id: int,
    current_user: AdminUser = Depends(auth_admin_handler.get_current_admin_user)
):
    """
    Xóa một bệnh nhân theo ID (chỉ dành cho admin).
    """
    delete_patient_by_id(patient_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)