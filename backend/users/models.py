from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateModel(BaseModel):
    username: str
    password: str
    full_name: str
    email: EmailStr
    phone: str
    role: str

class UserUpdateModel(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class UserResponseModel(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    phone: str
    role: str
