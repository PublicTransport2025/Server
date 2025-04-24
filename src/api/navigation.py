from typing import List

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import db_async_client
from src.schemas.navigation import RouteReport
from src.schemas.route import Route
from src.services.navigation import NavigationService

navigation_router = APIRouter(
    prefix="/navigation",
    tags=["Навигация"],
)


@navigation_router.get("/")
async def create_routes(from_id: int, to_id: int, session: AsyncSession = db_async_client) -> RouteReport:
    """

    """
    route_report = await NavigationService().create_routes(from_id, to_id, session)
    return route_report

@navigation_router.get("/bynumber", response_model=Route)
async def analyze_route(route_id: int):
    """
    Передает проанализированный маршрут
    :return:
    """
    pass
