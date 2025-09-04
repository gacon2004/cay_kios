from fastapi import HTTPException
from backend.database.connector import DatabaseConnector
from backend.auth.providers.auth_providers import AuthProvider
from backend.users.models import UserCreateModel, UserUpdateModel

auth_handler = AuthProvider()

def create_user(user_data: UserCreateModel):
    db = DatabaseConnector()
    hashed_pw = auth_handler.get_password_hash(user_data.password)
    result = db.call_procedure("sp_create_user", (
        user_data.username,
        hashed_pw,
        user_data.full_name,
        user_data.email,
        user_data.phone,
        user_data.role
    ))
    return result[0]

def get_all_users():
    db = DatabaseConnector()
    return db.call_procedure("sp_get_all_users")

def get_user_by_id(user_id: int):
    db = DatabaseConnector()
    result = db.call_procedure("sp_get_user_by_id", (user_id,))
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result[0]

def get_user_by_username(username: str):
    db = DatabaseConnector()
    result = db.call_procedure("sp_get_user_by_username", (username,))
    return result[0] if result else None

def update_user(user_id: int, update_data: UserUpdateModel):
    db = DatabaseConnector()
    result = db.call_procedure("sp_update_user", (
        user_id,
        update_data.full_name,
        update_data.email,
        update_data.phone,
        update_data.role
    ))
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result[0]

def delete_user(user_id: int):
    db = DatabaseConnector()
    result = db.call_procedure("sp_delete_user", (user_id,))
    return result[0]
