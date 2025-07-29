from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.patients.routers import router as user_router
from backend.auth.routers import router as auth_router
from backend.doctors.routers import router as doctor_router
from backend.patients.routers import router as patient_router
from backend.insurances.routers import router as insurance_router
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

# Set CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:4000",
    "http://localhost:19006",
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
app.include_router(auth_router)
app.include_router(doctor_router)
app.include_router(patient_router)
app.include_router(insurance_router)
# User APIs
app.include_router(user_router)
