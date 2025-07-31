from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.auth.providers.auth_providers import AuthProvider, AdminUser

from backend.services.controllers import (
    get_all_services, get_service_by_id,
    create_service, update_service, delete_service
)
from backend.services.models import (
    ServiceCreateModel, ServiceUpdateModel, ServiceResponseModel
)

auth_handler= AuthProvider()

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=list[ServiceResponseModel])
def api_get_all_services():
    return get_all_services()


@router.get("/{service_id}", response_model=ServiceResponseModel)
def api_get_service_by_id(service_id: int):
    return get_service_by_id(service_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def api_create_service(
    data: ServiceCreateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    create_service(data)
    return JSONResponse(status_code=201, content={"message": "Tạo dịch vụ thành công"})


@router.put("/", status_code=status.HTTP_200_OK)
def api_update_service(
    data: ServiceUpdateModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    update_service(data)
    return JSONResponse(status_code=200, content={"message": "Cập nhật dịch vụ thành công"})


@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def api_delete_service(
    service_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user)
):
    delete_service(service_id)
    return JSONResponse(status_code=200, content={"message": "Xoá dịch vụ thành công"})
