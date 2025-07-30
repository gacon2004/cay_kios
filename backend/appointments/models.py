from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreateModel(BaseModel):
    clinic_id: int
    service_id: int
    doctor_id: int

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

    class Config:
        from_attributes = True