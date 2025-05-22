from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.models.email_codes import EmailCode
from src.models.users import User
from src.schemas.token import Token, VKLogin
from src.schemas.user_auth import UserCreate
from src.services.auth import AuthService
from src.utils.email_sender import generate_code, send_email
from src.utils.security import create_tokens, hash_password, decode_token
from src.utils.users import decode_vk_id


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
    data = AuthService().login_user(db, form_data.username, form_data.password)
    return {"access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": data["expires_in"],
            "login": data["login"],
            "name": data["name"],
            "email": data["email"],
            "vk": data["vk"]}


@auth_router.post("/loginvk", response_model=Token)
async def loginvk(vklogin: VKLogin, db: Session = db_client):
    """
    Авторизация пользователя через ВК

    :param form_data: форма входа с логином и паролем
    :param db: сессия базы данных
    :return: access и refresh токены, а также время жизни access-токена
    """

    vkid, name = await decode_vk_id(vklogin.code_verifier, vklogin.code, vklogin.device_id, vklogin.state, False,
                                    get_name=True)
    vkid = str(vkid)
    user = db.query(User).filter(User.vkid == vkid).one_or_none()
    if user:
        if user.rang < 5:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account is blocked")
        access, refresh, expires_in = create_tokens(str(user.id))
        return {"access_token": access, "refresh_token": refresh, "expires_in": expires_in,
                "login": user.login, "name": user.name, "email": bool(user.login), "vk": bool(user.vkid)}
    else:
        user = User(name=name, rang=5, vkid=vkid)
        db.add(user)
        db.commit()
        db.refresh(user)
        access, refresh, expires_in = create_tokens(str(user.id))
        return {"access_token": access, "refresh_token": refresh, "expires_in": expires_in,
                "login": user.login, "name": user.name, "email": bool(user.login), "vk": bool(user.vkid)}


@auth_router.post("/refresh", response_model=Token)
def refresh(token: str = Header(...), db: Session = db_client):
    """
    Обновление пары токенов (access, refresh) по refresh токену

    :param token: refresh токен
    :param db: сессия базы данных
    :return: новые access и refresh токены и время жизни access токена
    """
    try:
        payload = decode_token(token)
        user = AuthService().get_user(db, payload["sub"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    access, refresh_token, expires_in = create_tokens(payload["sub"])
    return {"access_token": access,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "login": user.login,
            "name": user.name,
            "email": bool(user.login),
            "vk": bool(user.vkid)}


@auth_router.post("/signup", response_model=Token)
def signup(data: UserCreate, db: Session = db_client):
    """
    Регистрация нового пользователя

    :param data: модель с данными нового пользователя (имя, email, пароль)
    :param db: сессия базы данных
    :return: access и refresh токены, а также время жизни access токена
    """
    if db.query(User).filter(User.login == data.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Почта уже зарегистрирована")
    email_code = db.query(EmailCode).filter_by(email=data.email).first()

    if not email_code or email_code.code != data.code or datetime.utcnow() - email_code.created_at > timedelta(minutes=10):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неверный или просроченный код")
    
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
            "expires_in": expires_in,
            "login": user.login,
            "name": user.name,
            "email": bool(user.login),
            "vk": bool(user.vkid)}

@auth_router.post("/forgot-password")
def forgot_password(email: str, db: Session = db_client):
    """
    Запрос на сброс пароля — отправляет код на почту

    :param email: email пользователя
    :param db: сессия базы данных
    :return: сообщение об отправке кода
    """
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    code = generate_code()
    body = f"Ваш код сброса пароля: {code}"
    send_email(email, "Сброс пароля", body)

    existing = db.query(EmailCode).filter_by(email=email).first()
    if existing:
        existing.code = code
        existing.created_at = datetime.utcnow()
    else:
        db.add(EmailCode(email=email, code=code))

    db.commit()
    return {"message": "Код сброса пароля отправлен на почту"}


@auth_router.post("/reset-password")
def reset_password(email: str, code: str, new_password: str, db: Session = db_client):
    """
    Сброс пароля по email и коду

    :param email: email пользователя
    :param code: код подтверждения
    :param new_password: новый пароль
    :param db: сессия базы данных
    :return: сообщение об успешной смене пароля
    """
    record = db.query(EmailCode).filter_by(email=email).first()
    if not record or record.code != code or datetime.utcnow() - record.created_at > timedelta(minutes=10):
        raise HTTPException(400, "Неверный или просроченный код")

    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    user.hash_pass = hash_password(new_password)
    db.delete(record)
    db.commit()
    return {"message": "Пароль успешно изменён"}