from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from backend.auth.providers.auth_providers import AuthProvider
from backend.auth.controllers.auth_controller import signup_user, signin_user
from backend.auth.models.auth_models import (
    SignUpRequestModel,
    SignInRequestModel,
    UserAuthResponseModel,
    AccessTokenResponseModel,
)

router = APIRouter(prefix="/auth", tags=["Admin/Doctor Auth"])
auth_handler = AuthProvider()


@router.post("/signup", response_model=UserAuthResponseModel)
def signup_api(user_details: SignUpRequestModel):
    user = signup_user(user_details)
    access_token = auth_handler.create_access_token(user_id=user["id"], role=user["role"])
    refresh_token = auth_handler.encode_refresh_token(user["id"], role=user["role"])

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({
            "token": {"access_token": access_token, "refresh_token": refresh_token},
            "user": user
        })
    )

@router.post("/signin", response_model=UserAuthResponseModel)
def signin_api(user_details: SignInRequestModel):
    user = signin_user(user_details.username, user_details.password)
    access_token = auth_handler.create_access_token(user_id=user["id"], role=user["role"])
    refresh_token = auth_handler.encode_refresh_token(user["id"], role=user["role"])

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "token": {"access_token": access_token, "refresh_token": refresh_token},
            "user": user
        })
    )

@router.post("/refresh-token", response_model=AccessTokenResponseModel)
def refresh_token_api(refresh_token: str):
    new_token = auth_handler.refresh_token(refresh_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"access_token": new_token})
    )
