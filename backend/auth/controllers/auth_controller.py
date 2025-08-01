from fastapi import HTTPException
from backend.database.connector import DatabaseConnector
from backend.auth.providers.auth_providers import AuthProvider
from backend.auth.models.auth_models import SignUpRequestModel

auth_handler = AuthProvider()

def signup_user(user_model: SignUpRequestModel) -> dict:
    db = DatabaseConnector()

    existing = db.query_get("SELECT * FROM users WHERE username = %s", (user_model.username,))
    if existing:
        raise HTTPException(status_code=409, detail="Tài khoản đã tồn tại")

    hashed_password = auth_handler.get_password_hash(user_model.password)

    db.query_put(
        """
        INSERT INTO users (username, full_name, password_hash, role, email, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            user_model.username,
            user_model.full_name,
            hashed_password,
            user_model.role,
            user_model.email,
            user_model.phone,
        ),
    )

    user = db.query_get(
        """
        SELECT id, username, full_name, role, email, phone
        FROM users
        WHERE username = %s
        """,
        (user_model.username,),
    )[0]

    if user_model.role == "doctor":
        db.query_put(
            """
            INSERT INTO doctors (full_name, email, phone, specialty, user_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_model.full_name,
                user_model.email,
                user_model.phone,
                user_model.specialty,
                user["id"], 
            ),
        )

    return user

def signin_user(username: str, password: str) -> dict:
    db = DatabaseConnector()
    user = db.query_get("SELECT * FROM users WHERE username = %s", (username,))
    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")

    user = user[0]
    if not auth_handler.verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Sai mật khẩu")

    return user