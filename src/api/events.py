from typing import Optional

from fastapi import APIRouter, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.schemas.eventwrited import EventWrited
from src.services.events import EventsService

events_router = APIRouter(
    prefix="/events",
    tags=["Дорожные события"],
)


@events_router.post("/write")
async def create_event(data: EventWrited, token: str = Header(...), session: AsyncSession = db_async_client):
    """
    Записывает в базу данных новый пользовательский отзыв
    :param data: содержание отзыва
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Сообщение
    """
    event = await EventsService.write_event(session, token, data)
    return event


@events_router.get("/all")
async def get_all_stops(token: Optional[str] = Header(None), session: AsyncSession = db_async_client):
    """
    Передает список всех дорожных событий
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Список моделей дорожных событий
    """
    events = await EventsService.get_all_events(session, token)
    return events


@events_router.delete("/clear")
async def delete_event(event_id: str, token: str = Header(...), session: AsyncSession = db_async_client):
    """
    Удаляет остановку из избранного
    :param stop_id: айди остановки
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Модель обновленной остановки
    """
    event = await EventsService.clear_event(session, token, event_id)
    return event


@events_router.patch("/fix")
async def fix_event(event_id: str, token: str = Header(...), session: AsyncSession = db_async_client):
    """
    Удаляет остановку из избранного
    :param stop_id: айди остановки
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Модель обновленной остановки
    """
    event = await EventsService.fix_event(session, token, event_id)
    return event