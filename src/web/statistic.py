from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.core.db import db_client
from src.services.statistic import StatisticService

statistic_router = APIRouter(
    prefix="/statistic",
    tags=["Статистика"],
)
templates = Jinja2Templates(directory="templates")


@statistic_router.get('')
async def show_feedbacks(request: Request, db_session: Session = db_client):
    """
    Отображает страницу с отзывами
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    feedbacks, avg_mark = StatisticService().show_feedbacks(db_session)
    return templates.TemplateResponse("statistic.html",
                                      {"request": request, "feedbacks": feedbacks, "avg_mark": f"{avg_mark:.2f}"})


@statistic_router.delete('/{id}')
async def delete_feedback(request: Request, id: str, db_session: Session = db_client):
    """
    Обрабатывает запрос удаления отзыва
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)

    StatisticService().delete_feedback(id, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "Отзыв удален"}, status_code=200)
