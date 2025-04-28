from typing import List

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
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
