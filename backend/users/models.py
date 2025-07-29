from pydantic import BaseModel
from typing import Optional


class SignInRequestModel(BaseModel):
    username: str
    password: str


class UserSignUpRequestModel(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "admin"  # hoặc "receptionist"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class UserAuthResponseModel(BaseModel):
    token: TokenModel
    user: dict


class AccessTokenResponseModel(BaseModel):
    access_token: str
