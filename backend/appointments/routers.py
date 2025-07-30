from fastapi import APIRouter, Depends, Path
from typing import Annotated

from backend.auth.provider import AuthProvider
from backend.appointments.models import (
    AppointmentCreateModel,
    AppointmentResponseModel,
    AppointmentUpdateModel,
)
from backend.appointments.controllers import (
    create_appointment,
    get_my_appointments,
    update_appointment, 
    delete_appointment,
)

auth_handler = AuthProvider()

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=AppointmentResponseModel)
def register_appointment(
    data: AppointmentCreateModel,
    current_user: Annotated[dict, Depends(auth_handler.get_current_patient_user)]
):
    """
    Tạo một cuộc hẹn mới cho bệnh nhân đang đăng nhập
    """
    return create_appointment(current_user["id"], data)


@router.get("/me", response_model=list[AppointmentResponseModel])
def list_my_appointments(
    current_user: Annotated[dict, Depends(auth_handler.get_current_patient_user)]
):
    """
    Lấy danh sách cuộc hẹn của bệnh nhân đang đăng nhập
    """
    return get_my_appointments(current_user["id"])

@router.put("/appointments/{appointment_id}", tags=["Appointments"])
def admin_update_appointment(
    appointment_id: int = Path(...),
    data: AppointmentUpdateModel = Depends(),
    current_user: dict = Depends(AuthProvider.get_current_user),
):
    AuthProvider.require_admin(current_user)
    return update_appointment(appointment_id, data)

@router.delete("/appointments/{appointment_id}", tags=["Appointments"])
def admin_delete_appointment(
    appointment_id: int = Path(...),
    current_user: dict = Depends(AuthProvider.get_current_user),
):
    AuthProvider.require_admin(current_user)
    return delete_appointment(appointment_id)