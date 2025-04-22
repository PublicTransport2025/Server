from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.db import db_client

charts_router = APIRouter(
    prefix="/charts",
    tags=["Редактор остановок"],
)
templates = Jinja2Templates(directory="templates")


@charts_router.get('/test1')
async def test1(request: Request, db_session: Session = db_client):
    """
    Отображает редактор перегонов на карте
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    return 200
