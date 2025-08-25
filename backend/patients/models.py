from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime


# Model dùng để cập nhật thông tin bệnh nhân (partial update)
class PatientUpdateRequestModel(BaseModel):
    id: int  # Bắt buộc để xác định bệnh nhân cần cập nhật
    national_id: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    ward: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    occupation: Optional[str] = None
    ethnicity: Optional[str] = None

    @validator("national_id")
    def validate_national_id(cls, v):
        if v and len(v) != 12:
            raise ValueError("CCCD/CMND phải đúng 12 ký tự")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        if v and v.lower() not in {"male", "female", "other"}:
            raise ValueError("Giới tính phải là 'male', 'female' hoặc 'other'")
        return v


# Model dùng để trả dữ liệu bệnh nhân ra ngoài API
class PatientResponseModel(BaseModel):
    id: int
    national_id: Optional[str]
    full_name: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    phone: Optional[str]
    ward: Optional[str]
    district: Optional[str]
    province: Optional[str]
    occupation: Optional[str]
    ethnicity: Optional[str]
    created_at: Optional[datetime]

    class Config:
     from_attributes = True
