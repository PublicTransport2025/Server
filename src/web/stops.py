from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.constants import MAP_KEY
from src.core.db import db_client
from src.schemas.stop import StopUpd, StopInput
from src.services.stops import StopService

stops_router = APIRouter(
    prefix="/stops",
    tags=["Редактор остановок"],
)
templates = Jinja2Templates(directory="templates")


@stops_router.get('')
async def show_stops(request: Request, db_session: Session = db_client):
    """
    Отображает страницу редактора остановок
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    stops = StopService().show_stops(db_session)
    return templates.TemplateResponse("stops.html", {"request": request, "stops": stops, "map_key": MAP_KEY})


@stops_router.put('')
async def update_stop(request: Request, data: StopUpd, db_session: Session = db_client):
    """
    Обрабатывает форму обновления ООТ
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    StopService().update_stop(data, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "ООТ обновлена"}, status_code=200)


@stops_router.post('')
async def add_stop(request: Request, data: StopInput, db_session: Session = db_client):
    """
    Обрабатывает форму обновления ООТ
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    stop = StopService().add_stop(data, db_session, request.session['created_ip'], request.session['id'])
    return stop


@stops_router.post('/reset_tpu')
async def reset_tpu(request: Request, db_session: Session = db_client):
    """
    Распределение всех остановок по пересадочным узлам
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    StopService().reset_tpu(db_session, request.session['created_ip'], request.session['id'])
    return RedirectResponse("/web/stops", status_code=303)