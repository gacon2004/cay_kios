from pydantic import BaseModel
from backend.patients.models import PatientResponseModel
from typing import Optional
from datetime import date


#  Dùng CCCD/CMND để đăng nhập
class SignInRequestModel(BaseModel):
    national_id: str
    password: str


#  Dùng CCCD/CMND để đăng ký
class SignUpRequestModel(BaseModel):
    national_id: str
    password: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    ethnicity: Optional[str] = None


#  Access + refresh token
class TokenModel(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


#  Phản hồi sau khi đăng nhập thành công
class UserAuthResponseModel(BaseModel):
    token: TokenModel
    user: PatientResponseModel


#  Phản hồi nếu chỉ cần access token (refresh lại chẳng hạn)
class AccessTokenResponseModel(BaseModel):
    access_token: str
