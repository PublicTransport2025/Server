from fastapi import APIRouter

from src.web.io import io_router
from src.web.profile import profile_router

web_router = APIRouter(prefix="/web")

all_routers = [
    profile_router,
    io_router
]

for router in all_routers:
    web_router.include_router(router)
