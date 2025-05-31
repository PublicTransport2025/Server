from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.schemas.navigation import RouteReport
from src.services.navigation import NavigationService

navigation_router = APIRouter(
    prefix="/navigation",
    tags=["Навигация"],
)


def get_current_time() -> int:
    current_time = datetime.now()
    return current_time.hour * 60 + current_time.minute


@navigation_router.get("/")
async def create_routes(from_id: int, to_id: int, care: bool, change: bool, priority: int,
                        time: Optional[int] = None, current_time=Depends(get_current_time),
                        session: AsyncSession = db_async_client) -> RouteReport:
    """
    Обрабатывает запрос на построение маршрута
    :param from_id: начальная остановка
    :param to_id: конечная остановка
    :param care: только низкопольный пс?
    :param change: делать ли пересадки?
    :param priority: приоритет: 0 - загруженность, 1 - время, 2 - баланс
    :param time: время отправления
    :param current_time: текущее время
    :param session: сессия БД
    :return: json-модель маршрута
    """

    if time is None:
        time = current_time

    route_report = await NavigationService().create_routes(from_id, to_id, care, change, priority, time,
                                                           session)
    return route_report
