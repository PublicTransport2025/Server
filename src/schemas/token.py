from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Token(BaseModel):
    """
    Структура токенов, возвращаемых при авторизации и регистрации

    :param access_token: Токен доступа (JWT)
    :param refresh_token: Токен обновления (JWT)
    :param token_type: Тип токена (по умолчанию "bearer")
    :param login: Отображаемая почта пользователю
    :param name: Отображаемое имя пользователю
    :param email: Привязана ли почта?
    :param vk: Привязан ли ВК?
    :param expires_in: Время жизни access-токена в секундах
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    login: Optional[str] = None
    name: str
    email: bool
    vk: bool

class TokenPayload(BaseModel):
    """
    Payload, содержащий информацию, закодированную в токене

    :param sub: Идентификатор пользователя (user ID)
    :param exp: Время окончания действия токена (UTC datetime)
    """
    sub: str
    exp: datetime


class VKLogin(BaseModel):
    code_verifier: str
    state: str
    code: str
    device_id: str
