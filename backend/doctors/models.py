from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class DoctorUpdateRequestModel(BaseModel):
    id: int
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class DoctorResponseModel(BaseModel):
    id: int
    full_name: str
    specialty: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    created_at: Optional[datetime]