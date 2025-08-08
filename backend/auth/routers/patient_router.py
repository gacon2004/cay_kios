from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.auth.models.patient_models import (
    AccessTokenResponseModel,
    PatientResponseModel,
    CCCDRequestModel,
    PatientSignUpRequestModel,
    UserAuthResponseModel
)
from backend.auth.providers.partient_provider import PatientProvider
from backend.auth.controllers.patient_auth_controller import (
    issue_token_by_cccd,
    register_patient,
)

router = APIRouter(prefix="/auth/patient", tags=["Patient Auth"])
auth_handler = PatientProvider()


@router.post("/login", response_model=UserAuthResponseModel)
def token_by_cccd(user_cccd: CCCDRequestModel):
    """
    Bệnh nhân đăng nhập bằng CCCD — nếu chưa có thì trả lỗi.
    """
    result = issue_token_by_cccd(user_cccd.national_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result)
    )

@router.post("/register", response_model=UserAuthResponseModel)
def patient_register(user_details: PatientSignUpRequestModel):
    """
    Bệnh nhân đăng ký bằng form đầy đủ → lưu DB → trả access token.
    """
    user = register_patient(user_details)


    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(user)
    )


@router.post("/refresh-token", response_model=AccessTokenResponseModel)
def refresh_token_api(refresh_token: str):
    """
    Làm mới access token bằng refresh token.
    """
    new_token = auth_handler.refresh_token(refresh_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"access_token": new_token}),
    )
