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

# --- TOKEN MODEL ---
class TokenModel(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

# --- USER RESPONSE ---
class AdminDoctorResponseModel(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    email: EmailStr
    phone: str

# --- AUTH RESPONSE (FULL) ---
class UserAuthResponseModel(BaseModel):
    token: TokenModel
    user: AdminDoctorResponseModel

# --- ACCESS ONLY RESPONSE ---
class AccessTokenResponseModel(BaseModel):
    access_token: str