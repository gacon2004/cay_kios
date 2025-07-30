from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import các models cho OpenAPI, cần thiết cho openapi_extra
from fastapi.openapi.models import OAuthFlows, OAuthFlowPassword

# --- BẮT ĐẦU PHẦN CỦA AUTHENTICATION / SECURITY (Đã di chuyển lên trên) ---

from datetime import datetime, timedelta
from typing import Annotated, Optional
# Đảm bảo DatabaseConnector có sẵn và có thể import được
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
oauth2_scheme_admin_extractor = OAuth2PasswordBearer(
    tokenUrl="", # Đã đổi thành chuỗi rỗng
    scheme_name="AdminAuthExtractor" # Tên để phân biệt, không hiển thị trong Swagger UI
)

oauth2_scheme_patient_extractor = OAuth2PasswordBearer(
    tokenUrl="", # Đã đổi thành chuỗi rỗng
    scheme_name="PatientAuthExtractor" # Tên để phân biệt, không hiển thị trong Swagger UI
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

    def get_admin_user_by_id(self, user_id: int, db: DatabaseConnector) -> dict:
        user = db.query_get(
            """
            SELECT id, username, full_name, role
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        if not user: raise USER_NOT_FOUND_EXCEPTION
        return user[0]

# Khởi tạo instance của AuthProvider sau khi class đã được định nghĩa
auth_handler = AuthProvider()

# --- KẾT THÚC PHẦN CỦA AUTHENTICATION / SECURITY ---


# --- BẮT ĐẦU CẤU HÌNH FASTAPI APP ---
app = FastAPI(
    title="Example API",
    description="This is an example API of FastAPI",
    contact={
        "name": "Masaki Yoshiiwa",
        "email": "masaki.yoshiiwa@gmail.com",
    },
    # Áp dụng các scheme bảo mật mặc định cho Swagger UI
    # Chỉ hiển thị 'Bearer Auth' để dán token trực tiếp
    security=[{"Bearer Auth": []}],
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",

    openapi_extra={
        "securitySchemes": {
            "Bearer Auth": { # Tên này PHẢI khớp với tên trong 'security' ở trên
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT", # Khuyến nghị: mô tả định dạng token
                "description": "Nhập JWT Access Token vào đây (chỉ token, không có 'Bearer ' phía trước).",
            },
            # ĐÃ XÓA: PatientAuth và AdminAuth khỏi openapi_extra để chúng không xuất hiện
            # Nếu bạn muốn chúng xuất hiện, bạn phải định nghĩa chúng ở đây và trong 'security'
            # nhưng với tokenUrl là chuỗi rỗng như đã sửa trong provider.py.
        }
    }
)

# --- CẤU HÌNH ROUTERS VÀ MIDDLEWARE ---

# Import các routers của bạn
# LƯU Ý VỀ TRÙNG LẶP ROUTER:
# Nếu backend.patients.routers định nghĩa một APIRouter duy nhất,
# thì việc import nó hai lần với user_router và patient_router là không cần thiết
# và có thể gây nhầm lẫn hoặc xung đột nếu không có prefix rõ ràng.
# Hãy kiểm tra lại cấu trúc file của bạn.
from backend.patients.routers import router as user_router
from backend.auth.routers import router as auth_router
from backend.doctors.routers import router as doctor_router
from backend.patients.routers import router as patient_router # Có vẻ trùng với user_router?
from backend.insurances.routers import router as insurance_router
from backend.services.routers import router as services_router
from backend.clinics.routers import router as clinics_router
from backend.appointments.routers import router as appointments_router


# Auth APIs
app.include_router(auth_router)
app.include_router(doctor_router)
app.include_router(patient_router) # Nếu đây là router cho patient, hãy đặt prefix trong file router đó
app.include_router(insurance_router)
app.include_router(services_router)
app.include_router(clinics_router)
app.include_router(appointments_router)
# User APIs
app.include_router(user_router) # Nếu đây là router cho user chung, hãy đặt prefix trong file router đó


@app.get("/")
def root():
    return {"message": "Cay KIOS API is running!"}

# Set CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:4000",
    "http://localhost:19006",
    "*" # Thêm "*" tạm thời để dễ debug CORS, sau đó thu hẹp lại
]

# Set middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
