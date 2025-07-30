from fastapi import APIRouter, Depends
from typing import Annotated

from auth.provider import AuthProvider
from appointments.models import (
    AppointmentCreateModel,
    AppointmentResponseModel
)
from appointments.controllers import (
    create_appointment,
    get_my_appointments
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