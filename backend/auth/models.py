from pydantic import BaseModel, EmailStr
from patient.models.models import PatientResponseModel


class SignInRequestModel(BaseModel):
    email: str
    password: str


class SignUpRequestModel(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str


class UserAuthResponseModel(BaseModel):
    token: TokenModel
    user: PatientResponseModel


class AccessTokenResponseModel(BaseModel):
    access_token: str
