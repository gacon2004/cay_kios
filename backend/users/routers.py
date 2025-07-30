from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from auth.provider import AuthProvider
from users.controllers import register_user, signin_user
from users.models import (
    UserAuthResponseModel,
    SignInRequestModel,
    UserSignUpRequestModel,
    AccessTokenResponseModel,
)

router = APIRouter()
auth_handler = AuthProvider()


@router.post("/auth/user-signup", response_model=UserAuthResponseModel)
def signup_user(user_details: UserSignUpRequestModel):
    user = register_user(user_details)
    access_token = auth_handler.create_access_token(user_id=user["id"])
    refresh_token = auth_handler.encode_refresh_token(user["id"])

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({
            "token": {"access_token": access_token, "refresh_token": refresh_token},
            "user": user
        })
    )


@router.post("/auth/user-signin", response_model=UserAuthResponseModel)
def signin_user_api(user_details: SignInRequestModel):
    user = signin_user(user_details.username, user_details.password)
    access_token = auth_handler.create_access_token(user_id=user["id"])
    refresh_token = auth_handler.encode_refresh_token(user["id"])

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "token": {"access_token": access_token, "refresh_token": refresh_token},
            "user": user
        })
    )


@router.post("/auth/user-refresh-token", response_model=AccessTokenResponseModel)
def refresh_token_api(refresh_token: str):
    new_token = auth_handler.refresh_token(refresh_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"access_token": new_token})
    )
