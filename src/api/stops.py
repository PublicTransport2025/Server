from typing import List, Optional

from fastapi import APIRouter, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.schemas.stop import StopModel
from src.services.stops import StopService

stops_router = APIRouter(
    prefix="/stops",
    tags=["Остановки"],
)


@stops_router.get("/all", response_model=List[StopModel])
async def get_all_stops(token: Optional[str] = Header(None), session: AsyncSession = db_async_client):
    """
    Передает список всех остановок города
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Список моделей остановок
    """
    stops = await StopService.get_all_stops(session, token)
    return stops


@stops_router.post("/like", response_model=StopModel)
async def like_stop(stop_id: int, token: str = Header(...), session: AsyncSession = db_async_client):
    """
    Добавляет остановку в избранное
    :param stop_id: айди остановки
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Модель обновленной остановки
    """
    stop = await StopService.like_stop(session, token, stop_id)
    return stop


@stops_router.delete("/dislike", response_model=StopModel)
async def like_stop(stop_id: int, token: str = Header(...), session: AsyncSession = db_async_client):
    """
    Удаляет остановку из избранного
    :param stop_id: айди остановки
    :param token: Авторизационный токен пользователя
    :param session: Сессия БД
    :return: Модель обновленной остановки
    """
    stop = await StopService.dislike_stop(session, token, stop_id)
    return stop
