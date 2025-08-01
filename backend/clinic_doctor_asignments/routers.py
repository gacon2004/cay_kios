from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from backend.auth.providers.auth_providers import AuthProvider, AdminUser
from backend.clinic_doctor_asignments.models import (
    ClinicDoctorAssignmentResponse,
    ClinicDoctorAssignmentCreateRequest,
    ClinicDoctorAssignmentUpdateRequest,
)
from backend.clinic_doctor_asignments.controllers import (
    get_all_assignments,
    get_assignment_by_id,
    create_assignment,
    update_assignment,
    delete_assignment,
)

router = APIRouter()
auth_handler = AuthProvider()
OAuth2 = HTTPBearer()

router = APIRouter(prefix="/clinic-doctor-assignments", tags=["Clinic Doctor Assignments"])

@router.get("/", response_model=list[ClinicDoctorAssignmentResponse])
def get_all_assignments_api():
    rows = get_all_assignments()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(rows))


@router.get("/{assignment_id}", response_model=ClinicDoctorAssignmentResponse)
def get_assignment_api(
    assignment_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    row = get_assignment_by_id(assignment_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(row))


@router.post("/", response_model=ClinicDoctorAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment_api(
    data: ClinicDoctorAssignmentCreateRequest,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    new_id = create_assignment(data)
    created = get_assignment_by_id(new_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(created))


@router.put("/{assignment_id}", response_model=ClinicDoctorAssignmentResponse)
def update_assignment_api(
    assignment_id: int,
    data: ClinicDoctorAssignmentUpdateRequest,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    if assignment_id != data.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "ID trong URL và body không khớp"},
        )
    update_assignment(data)
    updated = get_assignment_by_id(assignment_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(updated))


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment_api(
    assignment_id: int,
    current_user: AdminUser = Depends(auth_handler.get_current_admin_user),
):
    delete_assignment(assignment_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
