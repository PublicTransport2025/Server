import os
from datetime import datetime, timedelta
from typing import Tuple
import jwt
from passlib.context import CryptContext

from src.core.constants import (
    JWT_SECRET_KEY, JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Хэширует пароль с помощью bcrypt

    :param password: исходный пароль
    :return: хэшированный пароль
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Проверяет, совпадает ли исходный пароль с хэшем

    :param plain: исходный пароль
    :param hashed: хэш пароля
    :return: True, если совпадают, иначе False
    """
    return pwd_context.verify(plain, hashed)

def create_tokens(user_id: str) -> Tuple[str, str, int]:
    """
    Создает access и refresh токены

    :param user_id: ID пользователя
    :return: кортеж (access_token, refresh_token, expires_in)
    """
    now = datetime.utcnow()
    acc_exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    ref_exp = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": acc_exp}
    access = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    payload["exp"] = ref_exp
    refresh = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    expires_in = int((acc_exp - now).total_seconds())
    return access, refresh, expires_in

def decode_token(token: str) -> dict:
    """
    Декодирует JWT токен

    :param token: JWT токен
    :return: полезная нагрузка токена (payload)
    :raises jwt.ExpiredSignatureError, jwt.InvalidTokenError: при ошибках токена
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
