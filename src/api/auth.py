from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from src.schemas.token import Token
from src.schemas.user_auth import UserLogin, UserCreate
from src.core.db import db_client
from src.services.auth import login_user
from src.models.users import User
from src.utils.security import create_tokens, hash_password, decode_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = db_client):
    """
    Авторизация пользователя

    :param form_data: форма входа с логином и паролем
    :param db: сессия базы данных
    :return: access и refresh токены, а также время жизни access-токена
    """
    data = login_user(db, form_data.username, form_data.password)
    return {"access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": data["expires_in"]}

@auth_router.post("/refresh", response_model=Token)
def refresh(token: str, db: Session = db_client):
    """
    Обновление пары токенов (access, refresh) по refresh токену

    :param token: refresh токен
    :param db: сессия базы данных
    :return: новые access и refresh токены и время жизни access токена
    """
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    access, refresh_token, expires_in = create_tokens(payload["sub"])
    return {"access_token": access,
            "refresh_token": refresh_token,
            "expires_in": expires_in}

@auth_router.post("/signup", response_model=Token)
def signup(data: UserCreate, db: Session = db_client):
    """
    Регистрация нового пользователя

    :param data: модель с данными нового пользователя (имя, email, пароль)
    :param db: сессия базы данных
    :return: access и refresh токены, а также время жизни access токена
    """
    if db.query(User).filter(User.login == data.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    user = User(
        name=data.name,
        login=data.email,
        hash_pass=hash_password(data.password),
        rang=5
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access, refresh_token, expires_in = create_tokens(str(user.id))
    return {"access_token": access,
            "refresh_token": refresh_token,
            "expires_in": expires_in}
