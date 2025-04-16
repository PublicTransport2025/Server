from typing import List

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.models.logistic import Stop
from src.schemas.coord import Coord
from src.schemas.stop import StopModel
from src.services.stops import StopService

stops_router = APIRouter(
    prefix="/stops",
    tags=["Остановки"],
)


@stops_router.get("/", response_model=List[StopModel])
async def get_all_stops(session: AsyncSession = db_async_client):
    """
    Передает список всех остановок города
    :return:
    """
    stops = await StopService.get_all_stops(session)
    return stops


@stops_router.get("/nearest", response_model=StopModel)
async def get_nearest_stop(lat: float, lon: float):
    """
    Передает ближайшую остановку к заданным координатам
    :return:
    """
    pass


@stops_router.post("/", response_model=int)
async def like_stop(stop_id: int):
    """
    Добавляет остановку в избранное
    :return:
    """
    pass


@stops_router.delete("/", response_model=int)
async def dislike_stop(stop_id: int):
    """
    Удаляет остановку из избранного
    :return:
    """
    pass
