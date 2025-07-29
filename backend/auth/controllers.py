from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.auth.provider import AuthProvider
from backend.auth.models import SignUpRequestModel
from backend.patients.controllers import get_patients_by_national_id

auth_handler = AuthProvider()


def register_user(patient_model: SignUpRequestModel):
    db = DatabaseConnector()

    # Kiểm tra national_id đã tồn tại chưa
    existing = get_patients_by_national_id(patient_model.national_id)
    if len(existing) != 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CCCD/CMND đã tồn tại trong hệ thống"
        )

    hashed_password = auth_handler.get_password_hash(patient_model.password)

    db.query_put(
        """
        INSERT INTO patients (
            national_id,
            full_name,
            date_of_birth,
            gender,
            phone,
            occupation,
            ethnicity,
            password_hash
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            patient_model.national_id,
            patient_model.full_name,
            patient_model.date_of_birth,
            patient_model.gender,
            patient_model.phone,
            patient_model.occupation,
            patient_model.ethnicity,
            hashed_password,
        ),
    )

    return {
        "national_id": patient_model.national_id,
        "full_name": patient_model.full_name,
    }


def signin_user(national_id: str, password: str):
    db = DatabaseConnector()

    user = db.query_get(
        """
        SELECT * FROM patients WHERE national_id = %s
        """,
        (national_id,),
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CCCD/CMND không tồn tại"
        )

    patient = user[0]

    if not auth_handler.verify_password(password, patient["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai mật khẩu"
        )

    # Tạo access token
    token = auth_handler.create_access_token(patient["id"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }
