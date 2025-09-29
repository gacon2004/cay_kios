from datetime import datetime, timedelta
from typing import Annotated, Optional
from backend.database.connector import DatabaseConnector
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

from dotenv import load_dotenv
load_dotenv()

OAUTH2_SCHEME_ADMIN = OAuth2PasswordBearer(
    tokenUrl="/auth/user-signin",
    scheme_name="AdminAuth"
)

OAUTH2_SCHEME_DOCTOR = OAuth2PasswordBearer(
    tokenUrl="/auth/doctor-signin",
    scheme_name="DoctorAuth"
)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Không thể xác thực thông tin đăng nhập, mật khẩu sai",
    headers={"WWW-Authenticate": "Bearer"},
)

USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Không tìm thấy người dùng",
)

class AdminUser(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

class DoctorUser(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

class AuthProvider:
    ALGORITHM = "HS256"
    TOKEN_EXPIRE_MINS = 300
    REFRESH_TOKEN_EXPIRE_HOURS = 10
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self) -> None:
        self.SECRET_KEY = os.getenv("APP_SECRET")
        if not self.SECRET_KEY:
            raise EnvironmentError("APP_SECRET environment variable not found")

    def verify_password(self, plain_password, hashed_password) -> bool:
        if isinstance(hashed_password, bytes):
            hashed_password = hashed_password.decode("utf-8")
        # Cắt ngắn mật khẩu xuống tối đa 72 byte để tránh lỗi ValueError từ bcrypt
        plain_password = plain_password[:72]
        return self.PWD_CONTEXT.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        # Cắt ngắn mật khẩu xuống tối đa 72 byte để tránh lỗi ValueError từ bcrypt
        password = password[:72]
        return self.PWD_CONTEXT.hash(password)

    def create_access_token(self, user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = {"sub": str(user_id), "role": role}
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.TOKEN_EXPIRE_MINS))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def encode_refresh_token(self, user_id: int, role: str) -> str:
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS),
            "iat": datetime.utcnow(),
            "scope": "refresh_token",
            "sub": str(user_id),
            "role": role,
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def refresh_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "refresh_token":
                user_id = int(payload["sub"])
                role = payload.get("role")
                return self.create_access_token(user_id, role)
            raise CREDENTIALS_EXCEPTION
        except JWTError:
            raise CREDENTIALS_EXCEPTION

    async def get_current_admin_user(self, token: Annotated[str, Depends(OAUTH2_SCHEME_ADMIN)]) -> dict:
        db = DatabaseConnector()
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = int(payload.get("sub"))
            role = payload.get("role")
            if not user_id or role not in ("admin", "receptionist"):
                raise CREDENTIALS_EXCEPTION
            user = self.get_admin_user_by_id(user_id, db)
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
            }
        except JWTError:
            raise CREDENTIALS_EXCEPTION

    async def get_current_doctor_user(self, token: Annotated[str, Depends(OAUTH2_SCHEME_DOCTOR)]) -> dict:
        db = DatabaseConnector()
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = int(payload.get("sub"))
            role = payload.get("role")
            if not user_id or role != "doctor":
                raise CREDENTIALS_EXCEPTION
            user = self.get_doctor_user_by_id(user_id, db)
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
            }
        except JWTError:
            raise CREDENTIALS_EXCEPTION

    def get_admin_user_by_id(self, user_id: int, db: DatabaseConnector) -> dict:
        user = db.query_get(
            "SELECT id, username, full_name, role FROM users WHERE id = %s",
            (user_id,),
        )
        if not user:
            raise USER_NOT_FOUND_EXCEPTION
        return user[0]

    def get_doctor_user_by_id(self, user_id: int, db: DatabaseConnector) -> dict:
        user = db.query_get(
            "SELECT id, username, full_name, role FROM users WHERE id = %s AND role = 'doctor'",
            (user_id,),
        )
        if not user:
            raise USER_NOT_FOUND_EXCEPTION
        return user[0]