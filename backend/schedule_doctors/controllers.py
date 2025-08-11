# backend/schedule_doctors/controllers.py
from __future__ import annotations
from fastapi import HTTPException
from typing import List
import json
from datetime import date

from backend.database.connector import DatabaseConnector
from backend.schedule_doctors.models import (
    ShiftCreateRequestModel,
    ShiftUpdateRequestModel,
    MonthBulkCreateRequestModel,
)

database = DatabaseConnector()

# -------- helpers --------
def _ensure_rows(rows: list[dict] | None, not_found_msg: str, code: int = 404) -> list[dict]:
    if not rows:
        raise HTTPException(status_code=code, detail=not_found_msg)
    return rows

def _build_update_json(payload: ShiftUpdateRequestModel) -> str:
    data = {k: v for k, v in payload.dict().items() if k != "id" and v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")
    return json.dumps(data, default=str)

# -------- use-cases --------
def create_shift_for_doctor(doctor_id: int, payload: ShiftCreateRequestModel) -> dict:
    rows = database.call_proc(
        "sp_schedule_create_shift",
        (
            doctor_id,
            payload.clinic_id,
            payload.work_date,
            payload.start_time,
            payload.end_time,
            payload.slot_minutes,
            payload.capacity_per_slot,
            payload.status,
            payload.note,
        ),
    )
    return _ensure_rows(rows, "Không tạo được ca làm việc", code=400)[0]

def update_shift_for_doctor(doctor_id: int, payload: ShiftUpdateRequestModel) -> dict:
    update_json = _build_update_json(payload)
    rows = database.call_proc("sp_schedule_update_shift", (doctor_id, payload.id, update_json))
    return _ensure_rows(rows, "Không tìm thấy ca hoặc không có quyền sửa")[0]

def delete_shift_for_doctor(doctor_id: int, shift_id: int) -> None:
    res = database.call_proc("sp_schedule_delete_shift", (doctor_id, shift_id))
    if res and isinstance(res[0], dict) and "affected" in res[0] and int(res[0]["affected"]) == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca hoặc không có quyền xóa")

def bulk_create_month_for_doctor(doctor_id: int, payload: MonthBulkCreateRequestModel) -> List[dict]:
    if not payload.days:
        raise HTTPException(status_code=400, detail="Danh sách ngày trống")
    if not payload.shift_templates:
        raise HTTPException(status_code=400, detail="Danh sách mẫu ca trống")

    rows = database.call_proc(
        "sp_schedule_bulk_create_month",
        (
            doctor_id,
            payload.clinic_id,
            payload.year,
            payload.month,
            json.dumps(payload.days),
            json.dumps([t.dict() for t in payload.shift_templates], default=str),
        ),
    )
    return rows or []

def get_calendar_month_for_doctor(doctor_id: int, clinic_id: int, year: int, month: int) -> List[dict]:
    return database.call_proc("sp_schedule_get_month", (doctor_id, clinic_id, year, month))

def get_calendar_day_for_doctor(doctor_id: int, clinic_id: int, day: date) -> List[dict]:
    return database.call_proc("sp_schedule_get_day", (doctor_id, clinic_id, day))
