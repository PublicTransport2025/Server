from typing import List

from fastapi import APIRouter

from src.schemas.route import Route

navigation_router = APIRouter(
    prefix="/navigation",
    tags=["Навигация"],
)


@navigation_router.get("/", response_model=List[Route])
async def create_route(start_stop_id: int, end_stop_id: int):
    """
    Передает список построенных маршрутов из точки А в точку Б
    :return:
    """
    pass

@navigation_router.get("/bynumber", response_model=Route)
async def analyze_route(route_id: int):
    """
    Передает проанализированный маршрут
    :return:
    """
    pass
