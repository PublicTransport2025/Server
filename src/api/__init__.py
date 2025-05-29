from fastapi import APIRouter, Header, HTTPException, Depends

from src.api.atp import atp_router
from src.api.auth import auth_router
from src.api.email_verification import email_router
from src.api.feedback import feedback_router
from src.api.navigation import navigation_router
from src.api.stops import stops_router
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
    stops_router,
    navigation_router,
    atp_router,
    auth_router,
    email_router,
    feedback_router
]

for router in all_routers:
    api_router.include_router(router)
