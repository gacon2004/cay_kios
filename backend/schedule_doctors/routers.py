from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from backend.auth.providers.auth_providers import AuthProvider, DoctorUser
from backend.schedule_doctors.models import (
    ShiftCreateRequestModel,
    MultiShiftBulkCreateRequestModel,
    ShiftResponseModel,
    CalendarDayDTO,
    DayShiftDTO,
)
from backend.schedule_doctors.controllers import (
    create_shift,
    bulk_create_shifts,
    get_calendar_days,
    get_day_shifts,
)

router = APIRouter(prefix="/schedule-doctors", tags=["Schedule Doctors"])
auth_handler = AuthProvider()
patient_handler = PatientProvider()

# Admin tạo 1 ca
@router.post("/shifts", response_model=ShiftResponseModel)
def api_create_shift(
    payload: ShiftCreateRequestModel,
    current_user: DoctorUser = Depends(auth_handler.get_current_doctor_user),
):
    data = create_shift(payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# Admin tạo nhiều ca (nhiều khung giờ/ngày)
@router.post("/shifts/bulk")
def api_bulk_create_shifts(
    payload: MultiShiftBulkCreateRequestModel,
    current_user: DoctorUser = Depends(auth_handler.get_current_doctor_user),
):
    data = bulk_create_shifts(payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# Bệnh nhân xem ngày trong tháng còn chỗ
@router.get("/calendar", response_model=List[CalendarDayDTO])
def api_calendar(
    doctor_id: int, 
    clinic_id: int, 
    month: str
):
    data = get_calendar_days(doctor_id, clinic_id, month)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# Bệnh nhân bấm vào 1 ngày -> lấy các CA (không còn slots)
@router.get("/day-shifts", response_model=List[DayShiftDTO])
def api_day_shifts(
    doctor_id: int, 
    clinic_id: int, 
    work_date: str,
):
    data = get_day_shifts(doctor_id, clinic_id, work_date)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))
