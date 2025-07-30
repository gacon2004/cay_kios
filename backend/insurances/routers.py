from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from insurances.controllers import (
    check_insurance_by_cccd,
    get_all_insurances,
    create_insurance,
    delete_insurance_by_id
)
from insurances.models import InsuranceCheckResponseModel, InsuranceCreateModel

router = APIRouter(prefix="/insurances", tags=["Insurances"])

@router.get("/check/{national_id}", response_model=InsuranceCheckResponseModel)
def check_insurance(national_id: str):
    result = check_insurance_by_cccd(national_id)
    return {"has_insurance": result}

@router.get("/")
def list_insurances():
    return get_all_insurances()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create(data: InsuranceCreateModel):
    return create_insurance(data)

@router.delete("/{insurance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(insurance_id: int):
    delete_insurance_by_id(insurance_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
