from datetime import datetime, timedelta
from typing import Annotated, Optional
from backend.database.connector import DatabaseConnector # Giả định đường dẫn này đúng
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

from dotenv import load_dotenv
load_dotenv()

# --- ĐÃ SỬA: Đổi tên biến và đặt tokenUrl thành chuỗi rỗng để Swagger UI không hiển thị form username/password ---
# Các instance này chỉ dùng để TRÍCH XUẤT TOKEN từ header cho FastAPI.
# ĐÃ XÓA scheme_name để chúng không tự động hiển thị trong Swagger UI.
oauth2_scheme_admin_extractor = OAuth2PasswordBearer(
    tokenUrl="", # Đã đổi thành chuỗi rỗng
    # scheme_name="AdminAuthExtractor" # ĐÃ XÓA DÒNG NÀY
)

oauth2_scheme_patient_extractor = OAuth2PasswordBearer(
    tokenUrl="", # Đã đổi thành chuỗi rỗng
    # scheme_name="PatientAuthExtractor" # ĐÃ XÓA DÒNG NÀY
)

# --- Exception Definitions ---
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Không thể xác thực thông tin đăng nhập, mật khẩu sai",
    headers={"WWW-Authenticate": "Bearer"},
)

USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Không tìm thấy người dùng",
)

# --- Token Payload and User Models ---
class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class AuthUser(BaseModel):
    id: int
    full_name: str
    national_id: str

class AdminUser(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

class AuthProvider:
    ALGORITHM = "HS256"
    TOKEN_EXPIRE_MINS = 30
    REFRESH_TOKEN_EXPIRE_HOURS = 10
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self) -> None:
        self.SECRET_KEY = os.getenv("APP_SECRET_STRING")
        if not self.SECRET_KEY:
            raise EnvironmentError("APP_SECRET_STRING environment variable not found")

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.PWD_CONTEXT.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        return self.PWD_CONTEXT.hash(password)

    # LƯU Ý: Các hàm này vẫn tự khởi tạo DatabaseConnector() bên trong.
    # Để chuẩn nghiệp vụ hơn, chúng nên nhận db_connector qua tham số (Dependency Injection).
    def authenticate_user(self, national_id: str, password: str) -> AuthUser:
        db = DatabaseConnector()
        user = self.get_user_by_national_id(national_id, db)
        if not user:
            raise USER_NOT_FOUND_EXCEPTION
        if not self.verify_password(password, user["password_hash"]):
            raise CREDENTIALS_EXCEPTION
        return AuthUser(id=user["id"], full_name=user["full_name"], national_id=user["national_id"])

    def create_access_token(self, user_id: int, role: str = "patient", expires_delta: Optional[timedelta] = None) -> str:
        to_encode = {"sub": str(user_id), "role": role}
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.TOKEN_EXPIRE_MINS))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def encode_refresh_token(self, user_id: int, role: str = "patient") -> str:
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
                role = payload.get("role", "patient")
                return self.create_access_token(user_id, role)
            raise CREDENTIALS_EXCEPTION
        except JWTError:
            raise CREDENTIALS_EXCEPTION

    # ĐÃ SỬA: Sử dụng các extractor mới
    async def get_current_patient_user(
        self, token: Annotated[str, Depends(oauth2_scheme_patient_extractor)]
    ) -> dict:
        db = DatabaseConnector()
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = int(payload.get("sub"))
            role = payload.get("role")
            if not user_id or role != "patient": raise CREDENTIALS_EXCEPTION
            user = self.get_user_by_id(user_id, db)
            return {"id": user["id"], "national_id": user["national_id"], "full_name": user["full_name"]}
        except JWTError: raise CREDENTIALS_EXCEPTION

    # ĐÃ SỬA: Sử dụng các extractor mới
    async def get_current_admin_user(
        self, token: Annotated[str, Depends(oauth2_scheme_admin_extractor)]
    ) -> dict:
        db = DatabaseConnector()
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = int(payload.get("sub"))
            role = payload.get("role")
            if not user_id or role not in ("admin", "receptionist"): raise CREDENTIALS_EXCEPTION
            user = self.get_admin_user_by_id(user_id, db)
            return {"id": user["id"], "username": user["username"], "full_name": user["full_name"], "role": user["role"]}
        except JWTError: raise CREDENTIALS_EXCEPTION

    def get_user_by_id(self, user_id: int, db_connector: DatabaseConnector) -> dict:
        user = db_connector.query_get(
            """
            SELECT id, national_id, full_name
            FROM patients
            WHERE id = %s
            """,
            (user_id,),
        )
        if not user: raise USER_NOT_FOUND_EXCEPTION
        return user[0]

    def get_user_by_national_id(self, national_id: str, db_connector: DatabaseConnector) -> dict:
        user = db_connector.query_get(
            """
            SELECT id, national_id, full_name, password_hash
            FROM patients
            WHERE national_id = %s
            """,
            (national_id,),
        )
        if not user: raise USER_NOT_FOUND_EXCEPTION
        return user[0]

    def get_admin_user_by_username(self, username: str, db: DatabaseConnector) -> dict:
        user = db.query_get(
            """
            SELECT id, username, full_name, password_hash, role
            FROM users
            WHERE username = %s
            """,
            (username,),
        )
        if not user: raise USER_NOT_FOUND_EXCEPTION
        return user[0]

    def get_admin_user_by_id(self, user_id: int, db_connector: DatabaseConnector) -> dict:
        user = db_connector.query_get(
            """
            SELECT id, username, full_name, role
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        if not user: raise USER_NOT_FOUND_EXCEPTION
        return user[0]

# Khởi tạo instance của AuthProvider
auth_handler = AuthProvider()
