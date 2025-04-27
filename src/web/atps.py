from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.schemas.atp import AtpModel, AtpInput
from src.services.atps import AtpService

atps_router = APIRouter(
    prefix="/atps",
    tags=["Редактор АТП"],
)
templates = Jinja2Templates(directory="templates")


@atps_router.get('')
async def show_atps(request: Request, db_session: Session = db_client):
    """
    Отображает страницу редактора АТП
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    atps = AtpService().show_atps(db_session)
    return templates.TemplateResponse("atps.html", {"request": request, "atps": atps})


@atps_router.put('')
async def update_atp(request: Request, data: AtpModel, db_session: Session = db_client):
    """
    Обрабатывает форму обновления АТП
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    AtpService().update_atp(data, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "АТП обновлено"}, status_code=200)


@atps_router.post('')
async def add_atp(request: Request, data: AtpInput, db_session: Session = db_client):
    """
    Обрабатывает форму добавления АТП
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    atp_model = AtpService().add_atp(data, db_session, request.session['created_ip'], request.session['id'])
    return atp_model


@atps_router.delete('/{id}')
async def delete_atp(request: Request, id: int, db_session: Session = db_client):
    """
    Обрабатывает запрос удаления АТП
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)

    AtpService.delete_atp(id, db_session, request.session['created_ip'], request.session['id'])
    return JSONResponse(content={"message": "АТП удалено"}, status_code=200)
