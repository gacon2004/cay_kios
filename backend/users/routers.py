from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from backend.users.models import UserCreateModel, UserUpdateModel, UserResponseModel
from backend.auth.providers.auth_providers import AuthProvider
from backend.users.controllers import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

router = APIRouter(prefix="/users", tags=["Users (Admin)"])
auth_handler = AuthProvider()

@router.get("/", response_model=list[UserResponseModel])
def list_users(current_user: dict = Depends(auth_handler.get_current_admin_user)):
    return get_all_users()

@router.get("/{user_id}", response_model=UserResponseModel)
def get_user(user_id: int, current_user: dict = Depends(auth_handler.get_current_admin_user)):
    return get_user_by_id(user_id)

@router.post("/", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
def create_new_user(user_data: UserCreateModel, current_user: dict = Depends(auth_handler.get_current_admin_user)):
    return create_user(user_data)

@router.put("/{user_id}", response_model=UserResponseModel)
def update_existing_user(user_id: int, data: UserUpdateModel, current_user: dict = Depends(auth_handler.get_current_admin_user)):
    return update_user(user_id, data)

@router.delete("/{user_id}")
def delete_existing_user(user_id: int, current_user: dict = Depends(auth_handler.get_current_admin_user)):
    return delete_user(user_id)
