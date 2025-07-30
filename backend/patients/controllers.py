from fastapi import HTTPException, status
from database.connector import DatabaseConnector
from auth.provider import AuthProvider, AuthUser
from patients.models import PatientUpdateRequestModel

auth_handler = AuthProvider()
database = DatabaseConnector()

def get_patient_profile(current_user: AuthUser) -> dict:
    db = DatabaseConnector()
    patient = db.query_get(
        """
        SELECT id, national_id, full_name, date_of_birth, gender, phone,
               occupation, ethnicity, created_at
        FROM patients
        WHERE id = %s
        """,
        (current_user.id,)
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bệnh nhân")
    return patient[0]

def update_patient(patient_model: PatientUpdateRequestModel) -> int:
    # Kiểm tra national_id đã tồn tại chưa
    existing = get_patients_by_national_id(patient_model.national_id)
    if len(existing) > 0 and existing[0]["id"] != patient_model.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CMND/CCCD đã tồn tại trong hệ thống",
        )

    update_fields = []
    params = []

    for field, value in patient_model.dict(exclude={"id"}).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if not update_fields:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    params.append(patient_model.id)

    sql = f"""
        UPDATE patients
        SET {", ".join(update_fields)}
        WHERE id = %s
    """
    return database.query_put(sql, tuple(params))
def get_all_patients(limit: int = 10, offset: int = 0) -> list[dict]:
    patients = database.query_get(
        """
        SELECT
            id,
            national_id,
            full_name,
            date_of_birth,
            gender,
            phone,
            occupation,
            ethnicity,
            created_at
        FROM patients
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )
    return patients
def get_patients_by_national_id(national_id: str) -> list[dict]:
    db = DatabaseConnector()
    return db.query_get(
        "SELECT * FROM patients WHERE national_id = %s",
        (national_id,),
    )
def get_patient_by_id(id: int) -> dict:
    result = database.query_get(
        """
        SELECT
            id,
            national_id,
            full_name,
            date_of_birth,
            gender,
            phone,
            occupation,
            ethnicity,
            created_at
        FROM patients
        WHERE id = %s
        """,
        (id,),
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bệnh nhân"
        )
    return result[0]
