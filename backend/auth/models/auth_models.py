from pydantic import BaseModel, EmailStr
from typing import Optional

class SignUpRequestModel(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "doctor"  # doctor | admin | receptionist
    email: EmailStr
    phone: str
    specialty: Optional[str] = None  # Chỉ sử dụng khi role == doctor

class SignInRequestModel(BaseModel):
    username: str
    password: str