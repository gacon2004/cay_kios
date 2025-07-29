from fastapi import HTTPException
from backend.database.connector import DatabaseConnector
from backend.insurances.models import InsuranceCreateModel

def check_insurance_by_cccd(national_id: str) -> bool:
    db = DatabaseConnector()
    result = db.query_get(
        "SELECT id FROM insurances WHERE national_id = %s",
        (national_id,)
    )
    return bool(result)

def get_all_insurances():
    db = DatabaseConnector()
    return db.query_get("SELECT * FROM insurances")

def create_insurance(data: InsuranceCreateModel):
    db = DatabaseConnector()
    
    # Check duplicate
    existing = db.query_get(
        "SELECT id FROM insurances WHERE national_id = %s",
        (data.national_id,)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Bệnh nhân đã có BHYT")

    db.query_put(
        """
        INSERT INTO insurances (national_id, insurance_number, expiry_date)
        VALUES (%s, %s, %s)
        """,
        (
            data.national_id,
            data.insurance_number,
            data.expiry_date
        )
    )
    return {"message": "Tạo bảo hiểm thành công"}

def delete_insurance_by_id(insurance_id: int):
    db = DatabaseConnector()
    db.query_put("DELETE FROM insurances WHERE id = %s", (insurance_id,))
