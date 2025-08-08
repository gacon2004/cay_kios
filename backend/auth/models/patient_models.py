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
    ward: Optional[str] = None   
    district: Optional[str] = None
    province: Optional[str] = None 
    occupation: Optional[str] = None
    ethnicity: Optional[str] = None

# --- TOKEN MODEL ---
class TokenModel(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

# --- USER RESPONSE ---
class PatientResponseModel(BaseModel):
    id: int
    national_id: str
    full_name: str

# --- AUTH RESPONSE (FULL) ---
class UserAuthResponseModel(BaseModel):
    token: TokenModel
    user: PatientResponseModel

# --- ACCESS ONLY RESPONSE ---
class AccessTokenResponseModel(BaseModel):
    access_token: str