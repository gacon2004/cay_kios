from fastapi import HTTPException
from backend.database.connector import DatabaseConnector
from backend.auth.providers.auth_providers import AuthProvider
from backend.users.models import UserCreateModel, UserUpdateModel

auth_handler = AuthProvider()

def get_all_users():
    db = DatabaseConnector()
    return db.query_get("SELECT id, username, full_name, email, phone, role FROM users")

def get_user_by_id(user_id: int):
    db = DatabaseConnector()
    user = db.query_get(
        "SELECT id, username, full_name, email, phone, role FROM users WHERE id = %s", (user_id,)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user[0]

def create_user(user_data: UserCreateModel):
    db = DatabaseConnector()
    if db.query_get("SELECT id FROM users WHERE username = %s", (user_data.username,)):
        raise HTTPException(status_code=409, detail="Username already exists")
    
    hashed_pw = auth_handler.get_password_hash(user_data.password)

    db.query_put(
        """
        INSERT INTO users (username, password_hash, full_name, email, phone, role)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_data.username, hashed_pw, user_data.full_name, user_data.email, user_data.phone, user_data.role)
    )

    return get_user_by_username(user_data.username)

def get_user_by_username(username: str):
    db = DatabaseConnector()
    user = db.query_get(
        "SELECT id, username, full_name, email, phone, role FROM users WHERE username = %s",
        (username,)
    )
    return user[0]

def update_user(user_id: int, update_data: UserUpdateModel):
    db = DatabaseConnector()
    user = get_user_by_id(user_id)  # raises if not found

    db.query_put(
        """
        UPDATE users
        SET full_name = %s, email = %s, phone = %s, role = %s
        WHERE id = %s
        """,
        (
            update_data.full_name or user["full_name"],
            update_data.email or user["email"],
            update_data.phone or user["phone"],
            update_data.role or user["role"],
            user_id
        )
    )

    return get_user_by_id(user_id)

def delete_user(user_id: int):
    db = DatabaseConnector()
    get_user_by_id(user_id)  # raises if not found
    db.query_put("DELETE FROM users WHERE id = %s", (user_id,))
    return {"message": "User deleted"}
