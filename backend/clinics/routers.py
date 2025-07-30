from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from clinics.models import (
    ClinicCreateModel,
    ClinicUpdateModel,
    ClinicResponseModel,
    ClinicDoctorResponseModel,
)
from clinics.controllers import (
    get_all_clinics,
    get_clinic_by_id,
    create_clinic,
    update_clinic,
    delete_clinic,
    get_clinics_by_service_id,
)

router = APIRouter(prefix="/clinics", tags=["Clinics"])


@router.get("/", response_model=list[ClinicResponseModel])
def list_clinics():
    return jsonable_encoder(get_all_clinics())


@router.get("/{clinic_id}", response_model=ClinicResponseModel)
def get_clinic(clinic_id: int):
    return jsonable_encoder(get_clinic_by_id(clinic_id))


@router.post(
    "/", response_model=ClinicResponseModel, status_code=status.HTTP_201_CREATED
)
def create_new_clinic(data: ClinicCreateModel):
    return jsonable_encoder(create_clinic(data))


@router.put("/{clinic_id}", response_model=ClinicResponseModel)
def update_existing_clinic(clinic_id: int, data: ClinicUpdateModel):
    return jsonable_encoder(update_clinic(clinic_id, data))


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_clinic(clinic_id: int):
    delete_clinic(clinic_id)
    return JSONResponse(status_code=204, content={})


@router.get("/by-service/{service_id}", response_model=list[ClinicDoctorResponseModel])
def list_clinics_by_service(service_id: int):
    return jsonable_encoder(get_clinics_by_service_id(service_id))
