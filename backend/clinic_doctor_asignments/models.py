from pydantic import BaseModel

class ClinicDoctorAssignmentBase(BaseModel):
    clinic_id: int
    doctor_id: int

class ClinicDoctorAssignmentCreateRequest(ClinicDoctorAssignmentBase):
    pass

class ClinicDoctorAssignmentUpdateRequest(ClinicDoctorAssignmentBase):
    id: int

class ClinicDoctorAssignmentResponse(ClinicDoctorAssignmentBase):
    id: int