from pydantic import BaseModel
from datetime import date

class InsuranceModel(BaseModel):
    id: int
    national_id: str
    insurance_number: str
    expiry_date: date

class InsuranceCreateModel(BaseModel):
    national_id: str
    insurance_number: str
    expiry_date: date

class InsuranceCheckResponseModel(BaseModel):
    has_insurance: bool
