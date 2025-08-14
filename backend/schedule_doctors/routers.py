from typing import List
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from backend.auth.providers.auth_providers import AuthProvider, DoctorUser, AdminUser
from backend.schedule_doctors.models import (
    CalendarDayDTO,
    DayShiftDTO,
    MultiShiftBulkCreateRequestModel,
    DayUpsertRequest,
    ShiftCreateRequestModel,
    ShiftResponseModel,
)
from backend.schedule_doctors.controllers import (
    get_calendar_days,
    get_day_shifts,
    create_shift_for_user,
    create_shift_for_doctor,
    bulk_create_shifts,
    bulk_create_shifts_for_doctor,
    update_day_shifts_for_user,
    update_day_shifts_for_doctor,
    delete_shifts_by_ids_for_user,
    delete_shifts_by_ids_for_doctor,
)

router = APIRouter(prefix="/schedule-doctors", tags=["Schedule Doctors"])
auth_handler = AuthProvider()
patient_handler = PatientProvider()

# =======================
# VIEW cho bệnh nhân
# =======================
@router.get("/calendar", response_model=List[CalendarDayDTO])
def api_calendar(doctor_id: int, clinic_id: int, month: str):
    data = get_calendar_days(doctor_id, clinic_id, month)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

@router.get("/day-shifts", response_model=List[DayShiftDTO])
def api_day_shifts(doctor_id: int, clinic_id: int, work_date: str):
    data = get_day_shifts(doctor_id, clinic_id, work_date)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# =======================
# TẠO 1 CA (single)
# =======================
@router.post("/shifts", response_model=ShiftResponseModel)
def api_create_shift_self(
    payload: ShiftCreateRequestModel,
    current_user: DoctorUser = Depends(auth_handler.get_current_doctor_user),
):
    data = create_shift_for_user(current_user, payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

@router.post("/shifts/{doctor_id}", response_model=ShiftResponseModel)
def api_create_shift_for_doctor_route(
    doctor_id: int,
    payload: ShiftCreateRequestModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    data = create_shift_for_doctor(doctor_id, payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# =======================
# TẠO NHIỀU NGÀY (bulk)
# =======================
@router.post("/shifts/bulk")
def api_bulk_create_shifts(
    payload: MultiShiftBulkCreateRequestModel,
    current_user: DoctorUser = Depends(auth_handler.get_current_doctor_user),
):
    data = bulk_create_shifts(payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

@router.post("/shifts/bulk/{doctor_id}")
def api_bulk_create_shifts_for_doctor_route(
    doctor_id: int,
    payload: MultiShiftBulkCreateRequestModel,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    data = bulk_create_shifts_for_doctor(doctor_id, payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# =======================
# UPDATE THEO NGÀY (schedule_id)
# =======================
@router.put("/day")
def api_day_update_self(
    payload: DayUpsertRequest,
    current_user: DoctorUser = Depends(auth_handler.get_current_doctor_user),
):
    data = update_day_shifts_for_user(current_user, payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

@router.put("/day/{doctor_id}")
def api_day_update_admin(
    doctor_id: int,
    payload: DayUpsertRequest,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    data = update_day_shifts_for_doctor(doctor_id, payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

# =======================
# DELETE THEO schedule_id (nhiều id một lần)
# =======================
@router.delete("/day")
def api_day_delete_self(
    clinic_id: int = Query(...),
    schedule_ids: List[int] = Query(..., description="repeat: ?schedule_ids=1&schedule_ids=2"),
    current_user: DoctorUser = Depends(auth_handler.get_current_doctor_user),
):
    data = delete_shifts_by_ids_for_user(current_user, clinic_id, schedule_ids)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

@router.delete("/day/{doctor_id}")
def api_day_delete_admin(
    doctor_id: int,
    clinic_id: int = Query(...),
    schedule_ids: List[int] = Query(..., description="repeat: ?schedule_ids=1&schedule_ids=2"),
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    data = delete_shifts_by_ids_for_doctor(doctor_id, clinic_id, schedule_ids)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(data))

