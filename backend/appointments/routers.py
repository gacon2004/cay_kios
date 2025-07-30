from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.responses import FileResponse
from auth.provider import AuthProvider
from appointments.models import (
    AppointmentCreateModel,
    AppointmentResponseModel
)
from appointments.controllers import (
    create_appointment,
    get_my_appointments,
    print_appointment_to_pdf
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

# In phiếu khám bệnh (xuất PDF)
@router.get("/{appointment_id}/print")
def print_appointment(
    appointment_id: int,
    current_user: Annotated[dict, Depends(auth_handler.get_current_patient_user)]
):
    from database.connector import DatabaseConnector
    db = DatabaseConnector()
    result = db.query_get("SELECT patient_id FROM appointments WHERE id = %s",(appointment_id,))
    if not result or result[0]["patient_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn của bạn hoặc không có quyền truy cập")
    pdf_path = print_appointment_to_pdf(appointment_id)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"phieu_kham_{appointment_id}.pdf")
