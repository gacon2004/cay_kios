from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from datetime import date

from backend.auth.providers.auth_providers import AuthProvider
from backend.schedule_doctors.models import (
    ShiftResponseModel,
    ShiftCreateRequestModel,
    ShiftUpdateRequestModel,
    MonthBulkCreateRequestModel,
)
from backend.schedule_doctors.controllers import (
    create_shift_for_doctor,
    update_shift_for_doctor,
    delete_shift_for_doctor,
    bulk_create_month_for_doctor,
    get_calendar_month_for_doctor,
    get_calendar_day_for_doctor,
)

router = APIRouter(prefix="/schedule-doctors", tags=["ScheduleDoctors"])
auth = AuthProvider()

# ---------------- CREATE ----------------
# POST /schedule-doctors
@router.post("", response_model=ShiftResponseModel)
def create_shift_api(
    payload: ShiftCreateRequestModel,
    current_user: dict = Depends(auth.get_current_doctor_user),
):
    row = create_shift_for_doctor(current_user["id"], payload)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(row))

# POST /schedule-doctors/month/bulk
@router.post("/month/bulk", response_model=List[ShiftResponseModel])
def bulk_create_month_api(
    payload: MonthBulkCreateRequestModel,
    current_user: dict = Depends(auth.get_current_doctor_user),
):
    rows = bulk_create_month_for_doctor(current_user["id"], payload)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(rows))

# ---------------- UPDATE (POST) ----------------
# POST /schedule-doctors/update
@router.post("/update", response_model=ShiftResponseModel)
def update_shift_api(
    payload: ShiftUpdateRequestModel,
    current_user: dict = Depends(auth.get_current_doctor_user),
):
    row = update_shift_for_doctor(current_user["id"], payload)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(row))

# ---------------- DELETE ----------------
# DELETE /schedule-doctors/{shift_id}
@router.delete("/{shift_id}", status_code=status.HTTP_200_OK)
def delete_shift_api(
    shift_id: int,
    current_user: dict = Depends(auth.get_current_doctor_user),
):
    delete_shift_for_doctor(current_user["id"], shift_id)
    return {"message": "Xóa ca làm việc thành công"}

# ---------------- READ (GET) ----------------
# GET /schedule-doctors/calendar/month?clinic_id=&year=&month=
@router.get("/calendar/month", response_model=List[ShiftResponseModel])
def calendar_month_api(
    clinic_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: dict = Depends(auth.get_current_doctor_user),
):
    rows = get_calendar_month_for_doctor(current_user["id"], clinic_id, year, month)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(rows))

# GET /schedule-doctors/calendar/day?clinic_id=&work_date=YYYY-MM-DD
@router.get("/calendar/day", response_model=List[ShiftResponseModel])
def calendar_day_api(
    clinic_id: int = Query(...),
    work_date: date = Query(...),
    current_user: dict = Depends(auth.get_current_doctor_user),
):
    rows = get_calendar_day_for_doctor(current_user["id"], clinic_id, work_date)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(rows))
