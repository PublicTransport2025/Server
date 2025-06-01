from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.constants import MAP_KEY
from src.core.db import db_client
from src.schemas.event import EventUpd, EventInput
from src.schemas.stop import StopUpd, StopInput
from src.services.events import EventsService
from src.services.stops import StopService

events_router = APIRouter(
    prefix="/events",
    tags=["Редактор событий"],
)
templates = Jinja2Templates(directory="templates")


@events_router.get('')
async def show_events(request: Request, db_session: Session = db_client):
    """
    Отображает страницу редактора дорожных событий
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    types = ["ДТП", "Дорожные работы", "Перекрытие движения"]
    lines = ["1 (в т.ч. выделенка)", "2", "3", "4", "все"]
    marks = ["модерация", "пользовательское", "отклонено", "отозвано", "официальное", "разрешено"]

    events = EventsService().show_events(db_session)
    return templates.TemplateResponse("events.html",
                                      {"request": request, "events": events, "types": types,
                                       "lines": lines, "marks": marks, "map_key": MAP_KEY})


@events_router.put('')
async def update_event(request: Request, data: EventUpd, db_session: Session = db_client):
    """
    Обрабатывает запрос редактирования дорожного события
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    EventsService().update_event(data, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "ООТ обновлена"}, status_code=200)


@events_router.post('')
async def add_event(request: Request, data: EventInput, db_session: Session = db_client):
    """
    Обрабатывает запрос добавления дорожного события
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    stop = EventsService().add_event(data, db_session, request.session['created_ip'], request.session['id'])
    return stop


@events_router.delete('/{id}')
async def delete_event(request: Request, id: str, db_session: Session = db_client):
    """
    Обрабатывает запрос удаления дорожного события
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)

    EventsService.delete_event(id, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "Дорожное событие удалено"}, status_code=200)

