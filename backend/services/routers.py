from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import List
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from backend.auth.providers.auth_providers import AuthProvider, AdminUser

from backend.services.controllers import (
    get_all_services, get_service_by_id,
    create_service, update_service, delete_service,
    get_my_services_by_user,
)
from backend.services.models import (
    ServiceCreateModel, ServiceUpdateModel, ServiceResponseModel
)

auth_handler= AuthProvider()

router = APIRouter(prefix="/services", tags=["Services"])


# API: Lấy danh sách dịch vụ (có thể filter theo bảo hiểm)
@router.get("/")
def list_services(
    has_insurances: Annotated[bool, Query(description="Có sử dụng bảo hiểm hay không")] = False
):
    return get_all_services(has_insurances)


# API: Lấy chi tiết 1 dịch vụ theo ID
@router.get("/{service_id}", response_model=ServiceResponseModel)
def api_get_service_by_id(service_id: int):
    return get_service_by_id(service_id)


# API: Lấy danh sách dịch vụ do bác sĩ hiện tại phụ trách
@router.get("/doctor/me", response_model=List[ServiceResponseModel])
def get_my_services(current_user = Depends(auth_handler.get_current_doctor_user)):
    if isinstance(current_user, dict):
        user_id = current_user.get("user_id", current_user.get("id"))
    else:
        user_id = getattr(current_user, "user_id", getattr(current_user, "id", None))

    if not user_id:
        raise HTTPException(status_code=401, detail="Token thiếu user_id")

    data = get_my_services_by_user(int(user_id))
    return jsonable_encoder(data)


# API: Tạo mới dịch vụ (chỉ admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
def api_create_service(
    data: ServiceCreateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    create_service(data)
    return JSONResponse(status_code=201, content={"message": "Tạo dịch vụ thành công"})


# API: Cập nhật dịch vụ (chỉ admin)
@router.put("/{service_id}", status_code=status.HTTP_200_OK)
def api_update_service(
    data: ServiceUpdateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    update_service(data)
    return JSONResponse(status_code=200, content={"message": "Cập nhật dịch vụ thành công"})


# API: Xoá 1 dịch vụ theo ID (chỉ admin)
@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def api_delete_service(
    service_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    delete_service(service_id)
    return JSONResponse(status_code=200, content={"message": "Xoá dịch vụ thành công"})
