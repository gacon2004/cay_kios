from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.auth.provider import AuthProvider
from backend.patients.models import PatientResponseModel
from backend.auth.models import SignUpRequestModel, UserAuthResponseModel, TokenModel

auth_handler = AuthProvider()

# Đăng Ký bệnh nhân, cấp token khi vừa đăng ký
def register_patient(data: SignUpRequestModel) -> UserAuthResponseModel:
    db = DatabaseConnector()

    existing = db.query_get(
        "SELECT id FROM patients WHERE national_id = %s",
        (data.national_id,)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Bệnh nhân đã tồn tại")

    db.query_put(
        """
        INSERT INTO patients (
            national_id, full_name, date_of_birth,
            gender, phone, occupation, ethnicity
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.national_id,
            data.full_name,
            data.date_of_birth,
            data.gender,
            data.phone,
            data.occupation,
            data.ethnicity,
        )
    )

    user = db.query_get(
        "SELECT id, national_id, full_name, date_of_birth, gender, phone, occupation, ethnicity, created_at FROM patients WHERE national_id = %s",
        (data.national_id,)
    )[0]

    access_token = auth_handler.create_access_token(user_id=user["id"], role="patient")
    refresh_token = auth_handler.encode_refresh_token(user["id"])

    return UserAuthResponseModel(
        token=TokenModel(
            access_token=access_token,
            refresh_token=refresh_token
        ),
        user=PatientResponseModel(**user)
    )

# Đăng nhập, cấp token bằng cccd

def issue_token_by_cccd(national_id: str) -> UserAuthResponseModel:
    db = DatabaseConnector()

    user = db.query_get(
        "SELECT id, national_id, full_name FROM patients WHERE national_id = %s",
        (national_id,)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bệnh nhân chưa đăng ký"
        )

    user = user[0]
    access_token = auth_handler.create_access_token(user_id=user["id"], role="patient")
    refresh_token = auth_handler.encode_refresh_token(user["id"])

    return {
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        "user": user
    }