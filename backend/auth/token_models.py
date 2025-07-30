from pydantic import BaseModel
from backend.patients.models import PatientResponseModel
from typing import Optional

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
