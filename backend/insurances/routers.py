from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from backend.auth.providers.auth_providers import AuthProvider, AdminUser
from backend.insurances.controllers import (
    get_all_insurances,
    create_insurance,
    delete_insurance_by_id,
    get_insurance_by_national_id
)
from backend.insurances.models import InsuranceCheckResponseModel, InsuranceCreateModel

auth_handler = AuthProvider()
router = APIRouter(prefix="/insurances", tags=["Insurances"])

@router.get("/check/{national_id}", response_model=InsuranceCheckResponseModel)
def check_insurance(national_id: str):
    """
    Công khai - kiểm tra bệnh nhân có BHYT theo CCCD.
    """
    result = get_insurance_by_national_id(national_id)
    return {"has_insurance": bool(result)}

@router.get("/")
def list_insurances(
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    """
    Chỉ admin được xem danh sách BHYT.
    """
    return get_all_insurances()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    data: InsuranceCreateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    """
    Chỉ admin hoặc lễ tân được thêm thông tin bảo hiểm.
    """
    return create_insurance(data)

@router.delete("/{insurance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    insurance_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    """
    Chỉ admin được xoá bảo hiểm.
    """
    delete_insurance_by_id(insurance_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
