from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from backend.auth.routers.patient_router import router as auth_patient_router
from backend.auth.routers.auth_router import router as auth_unified_router
from backend.doctors.routers import router as doctor_router
from backend.patients.routers import router as patient_router
from backend.insurances.routers import router as insurance_router
from backend.services.routers import router as services_router
from backend.clinics.routers import router as clinics_router
from backend.appointments.routers import router as appointments_router
from backend.clinic_doctor_asignments.routers import router as clinic_doctor_asignments_router
from backend.users.routers import router as users_router
from backend.schedule_doctors.routers import router as schedule_doctors_router
from backend.payments.routers import router as payments_router
from dotenv import load_dotenv
import os

load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Set API info
app = FastAPI(
    title="Example API",
    description="This is an example API of FastAPI",
    contact={
        "name": "Masaki Yoshiiwa",
        "email": "masaki.yoshiiwa@gmail.com",
    },
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
)

# Middleware set timezone +7
class TimezoneMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Thiết lập giờ VN (UTC+7)
        request.state.now = datetime.now(timezone(timedelta(hours=7)))
        response = await call_next(request)
        return response

# Đăng ký middleware
app.add_middleware(TimezoneMiddleware)

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
    "https://kiosk-lyart.vercel.app",
    "https://kiosk-admin-nu.vercel.app"
]

# Set middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth APIs
app.include_router(auth_patient_router)
app.include_router(auth_unified_router)
# Modul Api
app.include_router(doctor_router)
app.include_router(patient_router)
app.include_router(insurance_router)
app.include_router(services_router)
app.include_router(clinics_router)
app.include_router(appointments_router)
app.include_router(clinic_doctor_asignments_router)
app.include_router(schedule_doctors_router)
app.include_router(users_router)
app.include_router(payments_router)
