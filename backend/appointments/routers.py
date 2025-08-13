from fastapi import APIRouter, Depends, status, Query, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated

from backend.auth.providers.partient_provider import PatientProvider
from backend.appointments.models import (
    BookByShiftRequestModel, 
    AppointmentResponseModel,
    AppointmentFilterModel,
)
from backend.appointments.controllers import (
    book_by_shift_online,
    book_by_shift_offline,
    get_my_appointments,
    cancel_my_appointment,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])
auth_patient = PatientProvider()

# ONLINE (bệnh nhân thao tác)
@router.post("/online/book-by-shift", response_model=AppointmentResponseModel)
def api_book_by_shift_online(
    data: BookByShiftRequestModel,
    has_insurances: bool = Query(False, description="BHYT: true/false"),
    current_user: Annotated[dict, Depends(auth_patient.get_current_patient_user)] = None,
):
    detail = book_by_shift_online(current_user["id"], data, has_insurances)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))

# OFFLINE (bệnh nhân vẫn thao tác, ví dụ kiosk), khác mỗi channel để phân tích báo cáo
@router.post("/offline/book-by-shift", response_model=AppointmentResponseModel)
def api_book_by_shift_offline(
    data: BookByShiftRequestModel,
    has_insurances: bool = Query(False, description="BHYT: true/false"),
    current_user: Annotated[dict, Depends(auth_patient.get_current_patient_user)] = None,
):
    detail = book_by_shift_offline(current_user["id"], data, has_insurances)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))


@router.get("/me", response_model=list[AppointmentResponseModel])
def api_get_my_appointments(
    filters: AppointmentFilterModel = Depends(),
    current_user: Annotated[dict, Depends(auth_patient.get_current_patient_user)] = None,
):
    items = get_my_appointments(current_user["id"], filters)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(items))

# POST /appointments/{id}/cancel
@router.post("/{appointment_id}/cancel")
def api_cancel_my_appointment(
    appointment_id: int = Path(..., ge=1),
    current_user: Annotated[dict, Depends(auth_patient.get_current_patient_user)] = None,
):
    res = cancel_my_appointment(appointment_id, current_user["id"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(res))