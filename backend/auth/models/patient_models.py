from pydantic import BaseModel
from typing import Optional
from datetime import date

class CCCDRequestModel(BaseModel):
    national_id: str

class PatientSignUpRequestModel(BaseModel):
    national_id: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    ethnicity: Optional[str] = None
