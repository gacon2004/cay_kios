from pydantic import BaseModel
from typing import Optional

class ClinicCreateModel(BaseModel):
    name: str
    location: str
    status: str  # "active", "inactive", "closed"

class ClinicUpdateModel(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class ClinicResponseModel(BaseModel):
    id: int
    name: str
    location: str
    status: str

    class Config:
        from_attributes = True


# Model phản hồi kèm bác sĩ nếu cần mở rộng cho frontend
class ClinicDoctorResponseModel(ClinicResponseModel):
    # Bổ sung nếu cần show cả bác sĩ trong phòng
    pass
