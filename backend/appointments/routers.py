from fastapi import APIRouter, status, Depends, Path, Query
from typing import Annotated
from backend.auth.providers.auth_providers import AuthProvider
from backend.auth.providers.partient_provider import PatientProvider
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from backend.appointments.models import (
    AppointmentCreateModel,
    AppointmentResponseModel,
    AppointmentUpdateModel,
    AppointmentCancelResponse,
    AppointmentCreateBySlotModel
)
from backend.appointments.controllers import (
    create_appointment,
    get_my_appointments,
    update_appointment,
    delete_appointment,
    print_appointment_pdf,
    create_appointment_by_slot,
    cancel_appointment_by_patient
)

auth_admin_handler = AuthProvider()
auth_patient_handler = PatientProvider()

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=AppointmentResponseModel)
def register_appointment(
    data: AppointmentCreateModel,
    current_user: Annotated[dict, Depends(auth_patient_handler.get_current_patient_user)],
    has_insurances: Annotated[bool, Query(description="Có sử dụng bảo hiểm hay không")]
):
    """
    Tạo một cuộc hẹn mới cho bệnh nhân đang đăng nhập
    """
    return create_appointment(current_user["id"], has_insurances, data)


@router.get("/me", response_model=list[AppointmentResponseModel])
def list_my_appointments(
    current_user: Annotated[dict, Depends(auth_patient_handler.get_current_patient_user)]
):
    """
    Lấy danh sách cuộc hẹn của bệnh nhân đang đăng nhập
    """
    return get_my_appointments(current_user["id"])

@router.put("/{appointment_id}", tags=["Appointments"])
def admin_update_appointment(
    appointment_id: int = Path(...),
    data: AppointmentUpdateModel = Depends(),
    current_user: dict = Depends(AuthProvider.get_current_admin_user),
):
    return update_appointment(appointment_id, data)

@router.delete("/{appointment_id}", tags=["Appointments"])
def admin_delete_appointment(
    appointment_id: int = Path(...),
    current_user: dict = Depends(AuthProvider.get_current_admin_user),
):
    return delete_appointment(appointment_id)

@router.get("/{appointment_id}/print")
def print_pdf(
    appointment_id: int,
    current_user: Annotated[dict, Depends(auth_patient_handler.get_current_patient_user)],
    has_insurances: Annotated[bool, Query(description="Có sử dụng bảo hiểm hay không")]
):
    return print_appointment_pdf(appointment_id, has_insurances, current_user["id"])

# (1) Tạo lịch hẹn theo giờ đã chọn (slot)
@router.post("/slot", response_model=AppointmentResponseModel)
def create_my_appointment_by_slot(
    data: AppointmentCreateBySlotModel,
    current_user: Annotated[dict, Depends(auth_patient_handler.get_current_patient_user)]
):
    """
    Bệnh nhân tạo lịch theo slot_start đã chọn. 
    Trả về chi tiết AppointmentResponseModel.
    """
    detail = create_appointment_by_slot(current_user["id"], data)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))

# (2) Bệnh nhân hủy lịch của chính mình
@router.post("/{appointment_id}/cancel", response_model=AppointmentCancelResponse)
def cancel_my_appointment(
    appointment_id: int = Path(...),
    current_user: Annotated[dict, Depends(auth_patient_handler.get_current_patient_user)] = None
):
    """
    Bệnh nhân hủy lịch của chính mình. Chỉ cho hủy khi trạng thái còn hiệu lực.
    """
    res = cancel_appointment_by_patient(appointment_id, current_user["id"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(res))