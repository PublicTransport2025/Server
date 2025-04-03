from fastapi import APIRouter

from src.schemas.coord import Coord
from src.schemas.route import Route

routes_router = APIRouter(
    prefix="/routes",
    tags=["Маршруты"],
)

@routes_router.get("/")
async def get_all_routes():
    """
    Передает список всех маршрутов
    :return:
    """
    pass

@routes_router.get("/stopinfo")
async def get_stop_routes(stop_id: int):
    """
    Передает список маршрутов, проходящих через заданную остановку
    :return:
    """
    pass


@routes_router.post("/", response_model=int)
async def like_route(stop_id: int):
    """
    Добавляет маршрут в избранное
    :return:
    """
    pass

@routes_router.delete("/", response_model=int)
async def dislike_route(stop_id: int):
    """
    Удаляет маршрут из избранного
    :return:
    """
    pass