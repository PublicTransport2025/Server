from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.models.logistic import Route, Atp
from src.schemas.timetable import TimetableInput
from src.services.timetables import TimetableService

timetables_router = APIRouter(
    prefix="/timetables",
    tags=["Редактор расписания"],
)
templates = Jinja2Templates(directory="templates")


@timetables_router.get('/{id}')
async def show_timetables(request: Request, id: int, db_session: Session = db_client):
    """
    Отображает страницу редактора постоянных графиков
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    atps = db_session.query(Atp)

    routes = db_session.query(Route).where(Route.atp_id == id).order_by(Route.id).all()
    routes_dict = []
    for route in routes:
        timetables = []
        for timetable in route.timetables:
            timetables.append({'id': timetable.id, 'start': str(timetable.start)[:-3], 'lap': str(timetable.lap)[:-3]})
        timetables.sort(key=lambda t: t['start'])
        routes_dict.append({'id': route.id, 'number': route.number, 'label': route.label, 'timetables': timetables})
    return templates.TemplateResponse("timetables.html", {"request": request, "atps": atps, "routes": routes_dict})


@timetables_router.post('')
async def add_timetable(request: Request, data: TimetableInput, db_session: Session = db_client):
    """
    Обрабатывает апрос создания нового графика
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    timetable_model = TimetableService.add_timetable(data, db_session, request.session['created_ip'], request.session['id'])
    return timetable_model


@timetables_router.delete('/{id}')
async def delete_timetable(request: Request, id: int, db_session: Session = db_client):
    """
    Обрабатывает запрос удаления графика из расписания
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)

    TimetableService.delete_timetable(id, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "График удален"}, status_code=200)
