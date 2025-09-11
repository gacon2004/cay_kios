# backend/insurances/controllers.py
from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.insurances.models import InsuranceCreateModel

database = DatabaseConnector()

def call_procedure(proc_name: str, params: tuple = ()) -> list[dict]:
    return database.call_procedure(proc_name, params)

def get_all_insurances() -> list[dict]:
    return call_procedure("sp_get_all_insurances")

def get_insurance_by_national_id(national_id: str) -> list[dict]:
    return call_procedure("sp_get_insurance_by_national_id", (national_id,))

def create_insurance(data: InsuranceCreateModel):
    existing = get_insurance_by_national_id(data.national_id)
    if existing:
        raise HTTPException(status_code=409, detail="Bệnh nhân đã có BHYT")

    call_procedure("sp_create_insurance", (data.national_id, data.insurance_number, data.expiry_date))
    return {"message": "Tạo bảo hiểm thành công"}

def delete_insurance_by_id(insurance_id: int):
    call_procedure("sp_delete_insurance", (insurance_id,))
    return {"message": "Đã xóa bảo hiểm thành công"}
