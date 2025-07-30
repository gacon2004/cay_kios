from pydantic import BaseModel
from typing import Optional, List

class ServiceCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    price: int

class ServiceUpdateModel(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None

class ServiceResponseModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int

    class Config:
        from_attributes = True

class DoctorModel(BaseModel):
    id: int
    full_name: str
    specialty: Optional[str]

class ClinicModel(BaseModel):
    id: int
    name: str
    location: Optional[str]
    status: Optional[str]
    doctor: Optional[DoctorModel]

class ServiceWithClinicsModel(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Optional[int]
    clinics: List[ClinicModel] = []
    class Config:
        from_attributes = True