from typing import List

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.schemas.atp import AtpReport
from src.schemas.stop import StopModel
from src.services.atps import AtpService
from src.services.stops import StopService

atp_router = APIRouter(
    prefix="/atp",
    tags=["АТП"],
)


@atp_router.get("/", response_model=AtpReport)
async def get_atp_report(number: str, session: AsyncSession = db_async_client) -> AtpReport:
    """
    Передает список всех остановок города
    :return:
    """
    atp_report = await AtpService.route_report(number, session)
    return atp_report
