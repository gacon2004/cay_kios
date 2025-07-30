from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
from backend.clinic_doctor_asignments.models import (
    ClinicDoctorAssignmentCreateRequest,
    ClinicDoctorAssignmentUpdateRequest,
)

database = DatabaseConnector()

def get_all_assignments() -> list[dict]:
    sql = "SELECT id, clinic_id, doctor_id FROM clinic_doctor_assignments"
    return database.query_get(sql)

def get_assignment_by_id(id: int) -> dict:
    sql = "SELECT id, clinic_id, doctor_id FROM clinic_doctor_assignments WHERE id = %s"
    result = database.query_get(sql, (id,))
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy phân công")
    return result[0]

def create_assignment(data: ClinicDoctorAssignmentCreateRequest) -> int:
    sql = """
        INSERT INTO clinic_doctor_assignments (clinic_id, doctor_id)
        VALUES (%s, %s)
    """
    params = (data.clinic_id, data.doctor_id)
    return database.query_post(sql, params)

def update_assignment(data: ClinicDoctorAssignmentUpdateRequest) -> int:
    sql = """
        UPDATE clinic_doctor_assignments
        SET clinic_id = %s, doctor_id = %s
        WHERE id = %s
    """
    return database.query_put(sql, (data.clinic_id, data.doctor_id, data.id))

def delete_assignment(id: int) -> None:
    sql = "DELETE FROM clinic_doctor_assignments WHERE id = %s"
    affected = database.query_put(sql, (id,))
    if affected == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy phân công")
