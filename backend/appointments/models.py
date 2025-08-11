from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional

class AppointmentCreateModel(BaseModel):
    clinic_id: int
    service_id: int
    doctor_id: int

class AppointmentUpdateModel(BaseModel):
    clinic_id: Optional[int]
    doctor_id: Optional[int]
    appointment_time: Optional[datetime]
    status: Optional[str]

class AppointmentResponseModel(BaseModel):
    id: int
    patient_id: int
    clinic_id: int
    service_id: int
    doctor_id: int
    queue_number: int
    appointment_time: datetime
    qr_code: Optional[str]
    printed: bool
    status: Optional[str]
    service_name: str
    doctor_name: str
    clinic_name: str
    service_price: int
    cur_price : int

class AppointmentCreateBySlotModel(BaseModel):
    # patient_id sẽ gán từ token ở router, không nhận từ client
    patient_id: Optional[int] = None
    clinic_id: int
    service_id: int
    doctor_id: int
    slot_start: datetime
    price: float = 0.0

# --- MODEL MỚI: response hủy lịch ---
class AppointmentCancelResponse(BaseModel):
    ok: bool = True