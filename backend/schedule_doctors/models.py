from datetime import date, time
from typing import List, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator

# ====== REQUEST ======

class ShiftCreateRequestModel(BaseModel):
    doctor_id: int
    clinic_id: int
    work_date: date
    start_time: time
    end_time: time
    avg_minutes_per_patient: Annotated[int, Field(ge=5, le=120)] = 15
    max_patients: Annotated[int, Field(ge=1, le=200)]
    status: int = 1
    note: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def _end_after_start(cls, v: time, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time phải lớn hơn start_time")
        return v


class ShiftTimeConfig(BaseModel):
    start_time: time
    end_time: time
    avg_minutes_per_patient: Annotated[int, Field(ge=5, le=120)] = 15
    max_patients: Annotated[int, Field(ge=1, le=200)]
    status: int = 1
    note: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def _end_after_start(cls, v: time, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time phải lớn hơn start_time")
        return v


class MultiShiftBulkCreateRequestModel(BaseModel):
    doctor_id: int
    clinic_id: int
    start_date: date
    end_date: date
    weekdays: List[int] = Field(..., description="0=Mon .. 6=Sun")
    shifts: List[ShiftTimeConfig]

    @field_validator("end_date")
    @classmethod
    def _check_range(cls, v: date, info):
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("end_date phải >= start_date")
        return v

    @field_validator("weekdays")
    @classmethod
    def _check_weekdays(cls, v: List[int]):
        if not v:
            raise ValueError("weekdays không được rỗng")
        if any(d < 0 or d > 6 for d in v):
            raise ValueError("weekdays chỉ trong khoảng 0..6")
        return v


# ---- UPDATE THEO schedule_id ----
class ShiftEditItem(BaseModel):
    schedule_id: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    avg_minutes_per_patient: Optional[Annotated[int, Field(ge=5, le=120)]] = None
    max_patients: Optional[Annotated[int, Field(ge=1, le=200)]] = None
    status: Optional[int] = None
    note: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def _end_after_start(cls, v: Optional[time], info):
        st = info.data.get("start_time")
        if v is not None and st is not None and v <= st:
            raise ValueError("end_time phải lớn hơn start_time")
        return v


class DayUpsertRequest(BaseModel):
    clinic_id: int
    work_date: date
    # dùng ShiftEditItem để UPDATE theo schedule_id
    shifts: List[ShiftEditItem] = Field(..., min_items=1)

# ====== RESPONSE ======

TimeStr = Annotated[str, Field(pattern=r"^\d{2}:\d{2}:\d{2}$")]

class ShiftResponseModel(BaseModel):
    id: int
    doctor_id: int
    clinic_id: int
    work_date: date
    start_time: TimeStr
    end_time: TimeStr
    avg_minutes_per_patient: int
    max_patients: int
    booked_patients: int
    status: int
    note: Optional[str] = None


class CalendarDayDTO(BaseModel):
    work_date: date
    shifts_count: int
    total_capacity: int
    total_booked: int
    total_remaining: int


class DayShiftDTO(BaseModel):
    schedule_id: int
    start_time: TimeStr
    end_time: TimeStr
    avg_minutes_per_patient: int
    max_patients: int
    booked_patients: int
    remaining: int
    status: int
    note: Optional[str] = None
