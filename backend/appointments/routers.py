from fastapi import APIRouter, Depends, status, Query, Path, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated, List
from backend.auth.providers.auth_providers import AuthProvider
from backend.auth.providers.partient_provider import PatientProvider
from backend.appointments.models import (
    BookByShiftRequestModel, 
    AppointmentResponseModel,
    AppointmentFilterModel,
    AppointmentStatusUpdateModel,
    AppointmentCancelResponse,
    AppointmentPatientItem,
    AppointmentPaymentFilterModel,
    AppointmentAdminPaymentItem,
)
from backend.appointments.controllers import (
    book_by_shift_online,
    book_by_shift_offline,
    get_my_appointments,
    cancel_my_appointment,
    update_appointment_status_by_doctor,
    get_my_appointments_of_doctor_user,
    list_patient_appointments_by_payment,
    generate_visit_ticket_pdf,
    list_all_appointments_by_payment_admin,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])
auth_handler = AuthProvider()
patient_handler = PatientProvider()

# API: Đặt lịch khám online (bệnh nhân) - sử dụng lịch theo ca, có thể chọn BHYT
@router.post("/book-online", response_model=AppointmentResponseModel)
def api_book_by_shift_online(
    data: BookByShiftRequestModel,
    has_insurances: bool = Query(False, description="BHYT: true/false"),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    detail = book_by_shift_online(current_user["id"], data, has_insurances)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))


# API: Đặt lịch khám offline (bệnh nhân) - sử dụng lịch theo ca, có thể chọn BHYT
@router.post("/book-offline", response_model=AppointmentResponseModel)
def api_book_by_shift_offline(
    data: BookByShiftRequestModel,
    has_insurances: bool = Query(False, description="BHYT: true/false"),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    detail = book_by_shift_offline(current_user["id"], data, has_insurances)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))


# API: Lấy danh sách lịch hẹn của chính bệnh nhân đang đăng nhập
@router.get("/partient/me", response_model=list[AppointmentResponseModel])
def api_get_my_appointments(
    filters: AppointmentFilterModel = Depends(),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    items = get_my_appointments(current_user["id"], filters)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(items))


# API: Lấy danh sách lịch hẹn của bệnh nhân theo trạng thái thanh toán
@router.get("/patient/payment/me", response_model=List[AppointmentPatientItem])
def api_patient_my_appointments_payment(
    filters: AppointmentPaymentFilterModel = Depends(),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    data = list_patient_appointments_by_payment(current_user["id"], filters)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))


# API: Lấy danh sách lịch hẹn của bác sĩ đang đăng nhập
@router.get("/doctor/me")
def api_get_my_appointments_for_doctor(
    current_user = Depends(auth_handler.get_current_doctor_user)
):
    user_id = current_user.get("user_id", current_user.get("id")) if isinstance(current_user, dict) \
              else getattr(current_user, "user_id", getattr(current_user, "id", None))
    if not user_id:
        raise HTTPException(status_code=401, detail="Token thiếu user_id")

    data = get_my_appointments_of_doctor_user(int(user_id))
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))


# API: Bác sĩ cập nhật trạng thái lịch hẹn (confirmed, completed, cancelled, ...)
@router.put("/doctor/{appointment_id}/status")
def api_update_status_by_doctor(
    appointment_id: int = Path(..., ge=1),
    payload: AppointmentStatusUpdateModel = ...,
    current_user = Depends(auth_handler.get_current_doctor_user),
):
    user_id = current_user.get("user_id", current_user.get("id")) if isinstance(current_user, dict) \
              else getattr(current_user, "user_id", getattr(current_user, "id", None))
    if not user_id:
        raise HTTPException(status_code=401, detail="Token thiếu user_id")

    res = update_appointment_status_by_doctor(int(user_id), appointment_id, payload.status)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(res))


# API: Admin lấy danh sách tất cả lịch hẹn theo trạng thái thanh toán
@router.get("/admin/payment", response_model=List[AppointmentAdminPaymentItem])
def api_admin_list_appointments_by_payment(
    filters: AppointmentPaymentFilterModel = Depends(),
    current_admin = Depends(auth_handler.get_current_admin_user),
):
    data = list_all_appointments_by_payment_admin(filters)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))


# API: Bệnh nhân hủy lịch hẹn của chính mình
@router.post("/{appointment_id}/cancel", response_model=AppointmentCancelResponse)
def api_cancel_my_appointment(
    appointment_id: int = Path(..., ge=1),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    res = cancel_my_appointment(appointment_id, current_user["id"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(res))


# API: Bệnh nhân in phiếu khám (xuất file PDF cho lịch hẹn)
@router.get("/{appointment_id}/print-ticket", response_class=Response)
def api_print_ticket_pdf(
    appointment_id: int,
    current_user = Depends(patient_handler.get_current_patient_user),
):
    pdf_bytes, filename = generate_visit_ticket_pdf(appointment_id, current_user["id"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )
