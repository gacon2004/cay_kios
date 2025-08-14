from fastapi import APIRouter, Depends, status, Query, Path, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from backend.auth.providers.auth_providers import AuthProvider
from backend.auth.providers.partient_provider import PatientProvider
from backend.appointments.models import (
    BookByShiftRequestModel, 
    AppointmentResponseModel,
    AppointmentFilterModel,
    AppointmentCancelResponse,
)
from backend.appointments.controllers import (
    book_by_shift_online,
    book_by_shift_offline,
    get_my_appointments,
    cancel_my_appointment,
    get_my_appointments_of_doctor_user,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])
auth_handler = AuthProvider()
patient_handler = PatientProvider()

@router.post("/book-online", response_model=AppointmentResponseModel)
def api_book_by_shift_online(
    data: BookByShiftRequestModel,
    has_insurances: bool = Query(False, description="BHYT: true/false"),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    detail = book_by_shift_online(current_user["id"], data, has_insurances)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))

@router.post("/book-offline", response_model=AppointmentResponseModel)
def api_book_by_shift_offline(
    data: BookByShiftRequestModel,
    has_insurances: bool = Query(False, description="BHYT: true/false"),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    detail = book_by_shift_offline(current_user["id"], data, has_insurances)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(detail))

@router.get("/partient/me", response_model=list[AppointmentResponseModel])
def api_get_my_appointments(
    filters: AppointmentFilterModel = Depends(),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    items = get_my_appointments(current_user["id"], filters)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(items))

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

@router.post("/{appointment_id}/cancel", response_model=AppointmentCancelResponse)
def api_cancel_my_appointment(
    appointment_id: int = Path(..., ge=1),
    current_user: Annotated[dict, Depends(patient_handler.get_current_patient_user)] = None,
):
    res = cancel_my_appointment(appointment_id, current_user["id"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(res))
