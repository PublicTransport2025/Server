from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.users import User
from src.utils.security import verify_password, create_tokens


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Проверяет учетные данные пользователя

        :param db: сессия базы данных
        :param email: email пользователя
        :param password: пароль пользователя
        :return: объект пользователя, если аутентификация прошла успешно
        :raises HTTPException: если пользователь не найден или пароль неверен
        """
        user = db.query(User).filter(User.login == email).one_or_none()
        if not user or not user.hash_pass:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect login or password")
        if not verify_password(password, user.hash_pass):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect login or password")
        if user.rang < 5:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account is blocked")
        return user

    @staticmethod
    def login_user(db: Session, email: str, password: str):
        """
        Авторизует пользователя и возвращает JWT-токены

        :param db: сессия базы данных
        :param email: email пользователя
        :param password: пароль пользователя
        :return: access токен, refresh токен и время жизни access токена
        """
        user = AuthService.authenticate_user(db, email, password)
        access, refresh, expires_in = create_tokens(str(user.id))
        return {"access_token": access, "refresh_token": refresh, "expires_in": expires_in,
                "login": user.login, "name": user.name, "email": bool(user.login), "vk": bool(user.vkid)}

    @staticmethod
    def get_user(db: Session, id: str):
        """
        Выбирает пользователя из БД по его id

        :param db: сессия базы данных
        :param id: id пользователя
        :return: модель пользователя
        """
        user = db.query(User).filter(User.id == id).one()
        return user
