from pydantic import BaseModel
from typing import Optional

class ClinicCreateModel(BaseModel):
    name: str
    location: Optional[str] = None
    status: str  # "active", "inactive", "closed"

class ClinicUpdateModel(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class ClinicResponseModel(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    status: Optional[str] = None
    class Config:
        from_attributes = True


# Model phản hồi kèm bác sĩ nếu cần mở rộng cho frontend
class ClinicDoctorResponseModel(ClinicResponseModel):
    # Bổ sung nếu cần show cả bác sĩ trong phòng
    pass

class DoctorOut(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty: str
    phone: str

class ClinicOut(BaseModel):
    clinic_id: int
    clinic_name: str
    clinic_status: str
    doctor_id: int
    doctor_name: str
    specialty: str
    phone: str