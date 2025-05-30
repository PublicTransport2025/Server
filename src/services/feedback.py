import logging
import traceback

from fastapi import HTTPException
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import Feedback
from src.schemas.feedbackwrited import FeedbackWrited
from src.utils.security import decode_token


class FeedbackService:
    @staticmethod
    async def write_feedback(session: AsyncSession, token: str, data: FeedbackWrited) -> None:
        """
        Записывает в базу данных новый пользовательский отзыв
        :param data: содержание отзыва
        :param token: Авторизационный токен пользователя
        :param session: Сессия БД
        """
        payload = decode_token(token)
        user_id = payload["sub"]
        try:
            await session.execute(insert(Feedback).values(
                user_id=user_id,
                name=data.name,
                mark=data.mark,
                email=data.email,
                about=data.about))
            await session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
