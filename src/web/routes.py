from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.models.logistic import Route, Stop, Chart, Section
from src.schemas.route import SectionsInput, RouteModel, RouteInput
from src.services.routes import RouteService

routes_router = APIRouter(
    prefix="/routes",
    tags=["Редактор остановок"],
)
templates = Jinja2Templates(directory="templates")


@routes_router.get('')
async def show_routes(request: Request, db_session: Session = db_client):
    """
    Отображает страницу реестра маршрутов
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    routes = RouteService().show_routes(db_session)
    return templates.TemplateResponse("routes.html", {"request": request, "routes": routes})


@routes_router.post('')
async def add_route(request: Request, data: RouteInput, db_session: Session = db_client):
    """
    Форма добавления нового маршрута
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    route = RouteService().add_route(data, db_session, request.session['created_ip'], request.session['id'])
    return route


@routes_router.put('')
async def update_route(request: Request, data: RouteModel, db_session: Session = db_client):
    """
    Форма обновления существующего маршрута
    :param request: запрос сессии
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    RouteService().update_route(data, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "Маршрут обновлен"}, status_code=200)


@routes_router.get('/edit_route/{route_id}')
async def show_routes(request: Request, route_id: int, db_session: Session = db_client):
    """
    Отображает страницу реестра маршрутов
    :param request: запрос сессии
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    route = db_session.query(Route).filter_by(id=route_id).one()

    sections = db_session.query(Section).filter_by(route_id=route_id).order_by(Section.order).all()

    stop_models = db_session.query(Stop).order_by(Stop.name).all()
    stops = []
    for stop in stop_models:
        stops.append({'id': stop.id, 'name': f"{stop.name} ({stop.about})"})

    chart_models = db_session.query(Chart).order_by(Chart.label).all()
    charts = [{'id': 0, 'label': 'соединить прямой'}]
    for chart in chart_models:
        charts.append({'id': chart.id, 'label': chart.label})

    return templates.TemplateResponse("route.html", {"request": request, "sections": sections, "stops": stops,
                                                     "charts": charts, "id": route_id, "route": route})


@routes_router.post('/edit_route/{route_id}')
async def edit_route(request: Request, route_id: int, data: SectionsInput, db_session: Session = db_client):
    """
    Отображает страницу реестра маршрутов
    :param request: запрос сессии
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    RouteService().edit_route(route_id, data, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "Остановки маршрута сохранены"}, status_code=200)
