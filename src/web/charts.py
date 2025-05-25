from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.constants import MAP_KEY
from src.core.db import db_client
from src.models.logistic import Stop, Chart
from src.schemas.charts import ChartInput, ChartUpd
from src.services.charts import ChartService

charts_router = APIRouter(
    prefix="/charts",
    tags=["Редактор Карт"],
)
templates = Jinja2Templates(directory="templates")


@charts_router.get('')
async def show_charts(request: Request, db_session: Session = db_client):
    """
    Отображает страницу редактора схем движения
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    stop_models = db_session.query(Stop).order_by(Stop.name).all()
    stops = []
    for stop in stop_models:
        stops.append({'id': stop.id, 'name': f"{stop.name} ({stop.about})", "lat": stop.lat, "lon": stop.lon})

    chart_models = db_session.query(Chart).order_by(Chart.id).all()
    charts = []
    for chart in chart_models:
        charts.append(
            {'id': chart.id, 'label': chart.label, "lats_str": " ".join(map(str, chart.lats)),
             "lons_str": " ".join(map(str, chart.lons))})

    return templates.TemplateResponse("charts.html", {"request": request, "map_key": MAP_KEY, "stops": stops, "charts": charts})


@charts_router.put('')
async def update_chart(request: Request, data: ChartUpd, db_session: Session = db_client):
    """
    Обрабатывает форму обновления cхемы движения
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    ChartService().update_chart(data, db_session, request.session['created_ip'], request.session['id'])



@charts_router.post('')
async def add_chart(request: Request, data: ChartInput, db_session: Session = db_client):
    """
    Обрабатывает форму добавления схемы движения
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    ChartService().add_chart(data, db_session, request.session['created_ip'], request.session['id'])


@charts_router.delete('/{id}')
async def delete_chart(request: Request, id: int, db_session: Session = db_client):
    """
    Обрабатывает запрос удаления АТП
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)

    ChartService.delete_chart(id, db_session, request.session['created_ip'], request.session['id'])

