from fastapi import APIRouter, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.schemas.feedbackwrited import FeedbackWrited
from src.services.feedback import FeedbackService

feedback_router = APIRouter(
    prefix="/feedback",
    tags=["Отзывы"],
)


@feedback_router.post("/write")
async def write_feedback(data: FeedbackWrited, token: str = Header(...), session: AsyncSession = db_async_client):
    """
    Записывает в базу данных новый пользовательский отзыв
    :param data: содержание отзыва
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Сообщение
    """
    await FeedbackService.write_feedback(session, token, data)
    return {"message": "Feedback saved"}
