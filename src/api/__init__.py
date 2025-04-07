from fastapi import APIRouter, Header, HTTPException, Depends

from src.api.admin import admin_router
from src.api.events import events_router
from src.api.navigation import navigation_router
from src.api.operator import operator_router
from src.api.routes import routes_router
from src.api.statistic import statistic_router
from src.api.stops import stops_router
from src.api.timetables import timetables_router
from src.api.users import users_router
from src.core.constants import API_KEY, VERSION


def verify_api_key(api_key: str = Header(...)) -> None:
    """
    Функция проверки доступа апи
    :param api_key: кодовая фраза
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid code phrase")


if VERSION == "DEBUG":
    api_router = APIRouter(prefix="/api")
else:
    api_router = APIRouter(prefix="/api", dependencies=[Depends(verify_api_key)])


all_routers = [
    users_router,
    stops_router,
    routes_router,
    timetables_router,
    navigation_router,
    events_router,
    operator_router,
    admin_router,
    statistic_router
]

for router in all_routers:
    api_router.include_router(router)
