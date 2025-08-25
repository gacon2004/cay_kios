from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from backend.auth.providers.auth_providers import AuthProvider, AdminUser
from backend.services.controllers import (
    get_all_services,
    get_service_by_id,
    create_service,
    update_service,
    delete_service,
    get_my_services_by_user,
)
from backend.services.models import (
    ServiceCreateModel,
    ServiceUpdateModel,
    ServiceResponseModel,
)

auth_handler = AuthProvider()

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=List[ServiceResponseModel])
def api_get_all_services():
    """Lấy danh sách tất cả dịch vụ"""
    result = get_all_services()
    return jsonable_encoder(result)


@router.get("/{service_id}", response_model=ServiceResponseModel)
def api_get_service_by_id(service_id: int):
    """Lấy chi tiết dịch vụ theo ID"""
    result = get_service_by_id(service_id)
    return jsonable_encoder(result)


@router.get("/doctor/me", response_model=List[ServiceResponseModel])
def api_get_my_services(current_user=Depends(auth_handler.get_current_doctor_user)):
    """Lấy danh sách dịch vụ của bác sĩ hiện tại"""
    user_id = None
    if isinstance(current_user, dict):
        user_id = current_user.get("user_id", current_user.get("id"))
    else:
        user_id = getattr(current_user, "user_id", getattr(current_user, "id", None))

    if not user_id:
        raise HTTPException(status_code=401, detail="Token thiếu user_id")

    result = get_my_services_by_user(int(user_id))
    return jsonable_encoder(result)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ServiceResponseModel)
def api_create_service(
    data: ServiceCreateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    """Tạo dịch vụ mới"""
    result = create_service(data)
    return jsonable_encoder(result)


@router.put("/", status_code=status.HTTP_200_OK, response_model=ServiceResponseModel)
def api_update_service(
    data: ServiceUpdateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    """Cập nhật dịch vụ"""
    result = update_service(data)
    return jsonable_encoder(result)


@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def api_delete_service(
    service_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    """Xóa dịch vụ"""
    delete_service(service_id)
    return JSONResponse(status_code=200, content={"message": "Xóa dịch vụ thành công"})
