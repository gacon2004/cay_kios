from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime

# ----- RESPONSE -----
class ShiftResponseModel(BaseModel):
    id: int
    doctor_id: int
    clinic_id: int
    work_date: date
    start_time: time
    end_time: time
    slot_minutes: int
    capacity_per_slot: int
    status: str
    note: Optional[str] = None
    created_at: Optional[datetime] = None

# ----- CREATE / UPDATE -----
class ShiftBase(BaseModel):
    clinic_id: int
    work_date: date
    start_time: time
    end_time: time
    slot_minutes: int = Field(15, ge=5, le=240)
    capacity_per_slot: int = Field(1, ge=1, le=50)
    status: str = "OPEN"
    note: Optional[str] = None

class ShiftCreateRequestModel(ShiftBase):
    """Tạo 1 ca trong 1 ngày"""

class ShiftUpdateRequestModel(BaseModel):
    id: int
    # các field optional; chỉ truyền field cần sửa
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_minutes: Optional[int] = Field(None, ge=5, le=240)
    capacity_per_slot: Optional[int] = Field(None, ge=1, le=50)
    status: Optional[str] = None
    note: Optional[str] = None

# ----- BULK BY MONTH -----
class ShiftTemplate(BaseModel):
    start_time: time
    end_time: time
    slot_minutes: int = Field(15, ge=5, le=240)
    capacity_per_slot: int = Field(1, ge=1, le=50)
    status: str = "OPEN"
    note: Optional[str] = None

class MonthBulkCreateRequestModel(BaseModel):
    clinic_id: int
    year: int
    month: int
    days: List[int]                 # ví dụ [1,2,3,10,17,24]
    shift_templates: List[ShiftTemplate]  # danh sách mẫu ca áp cho từng ngày
