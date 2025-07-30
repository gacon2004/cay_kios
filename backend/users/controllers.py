from fastapi import HTTPException, status
from database.connector import DatabaseConnector
from auth.provider import AuthProvider
from users.models import UserSignUpRequestModel


auth_handler = AuthProvider()

def register_user(user_model: UserSignUpRequestModel):
    db = DatabaseConnector()

    existing = db.query_get(
        "SELECT * FROM users WHERE username = %s", (user_model.username,)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Tài khoản đã tồn tại")

    hashed_password = auth_handler.get_password_hash(user_model.password)

    db.query_put(
        """
        INSERT INTO users (username, full_name, password_hash, role)
        VALUES (%s, %s, %s, %s)
        """,
        (
            user_model.username,
            user_model.full_name,
            hashed_password,
            user_model.role,
        ),
    )

    user = db.query_get(
        "SELECT id, username, full_name, role FROM users WHERE username = %s",
        (user_model.username,),
    )[0]

    return user


def signin_user(username: str, password: str):
    db = DatabaseConnector()

    user = db.query_get("SELECT * FROM users WHERE username = %s", (username,))
    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")

    user = user[0]

    if not auth_handler.verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Sai mật khẩu")

    return user
