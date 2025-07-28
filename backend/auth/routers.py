from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from auth.provider import AuthProvider
from auth.controllers import (
    register_user,
    signin_user,
)
from auth.models import (
    UserAuthResponseModel,
    SignInRequestModel,
    SignUpRequestModel,
    AccessTokenResponseModel,
)

router = APIRouter()
auth_handler = AuthProvider()


@router.post("/v1/auth/signup", response_model=UserAuthResponseModel)
def signup_api(user_details: SignUpRequestModel):
    """
    API đăng ký tài khoản mới bằng CCCD/CMND.
    """
    user = register_user(user_details)  # user trả về phải chứa "id", "national_id", "full_name"
    access_token = auth_handler.create_access_token(user_id=user["id"])
    refresh_token = auth_handler.encode_refresh_token(user["id"])

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({
            "token": {"access_token": access_token, "refresh_token": refresh_token},
            "user": user
        }),
    )


@router.post("/v1/auth/signin", response_model=UserAuthResponseModel)
def signin_api(user_details: SignInRequestModel):
    """
    API đăng nhập bằng CCCD/CMND và mật khẩu.
    """
    user = signin_user(user_details.national_id, user_details.password)
    access_token = auth_handler.create_access_token(user_id=user.id)
    refresh_token = auth_handler.encode_refresh_token(user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "token": {"access_token": access_token, "refresh_token": refresh_token},
            "user": user
        }),
    )


@router.post("/v1/auth/refresh-token", response_model=AccessTokenResponseModel)
def refresh_token_api(refresh_token: str):
    """
    API làm mới access token bằng refresh token.
    """
    new_token = auth_handler.refresh_token(refresh_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"access_token": new_token}),
    )
