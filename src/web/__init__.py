from fastapi import APIRouter

from src.web.admins import admins_router
from src.web.atps import atps_router
from src.web.charts import charts_router
from src.web.io import io_router
from src.web.logs import logs_router
from src.web.profile import profile_router
from src.web.routes import routes_router
from src.web.statistic import statistic_router
from src.web.stops import stops_router
from src.web.timetables import timetables_router

web_router = APIRouter(prefix="/web")

all_routers = [
    profile_router,
    io_router,
    stops_router,
    routes_router,
    atps_router,
    timetables_router,
    logs_router,
    admins_router,
    charts_router,
    statistic_router
]

for router in all_routers:
    web_router.include_router(router)
