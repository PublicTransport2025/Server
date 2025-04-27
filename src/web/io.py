from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.services.io import IOService

io_router = APIRouter(
    prefix="/io",
    tags=["Экспорт/Импорт"],
)
templates = Jinja2Templates(directory="templates")


@io_router.get('')
async def import_output(request: Request):
    """
    Отображает страницу экспорта и импорта данных
    :param request: запрос сессии
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")
    return templates.TemplateResponse("io.html", {"request": request})


@io_router.post('/upload/{source}')
async def upload_table(request: Request, source: str, table: UploadFile, db_session: Session = db_client):
    """
    Обработчик формы загрузки страницы

    :param request: запрос сессии
    :param source: название таблицы
    :param table: ксв-файл
    :param db_session: сессия БД
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)
    contents = await table.read()
    IOService.upload_table(contents, source, db_session, request.session['created_ip'], request.session['id'])
    return RedirectResponse("/web/io", status_code=303)


@io_router.get('/download/{source}')
async def download_table(request: Request, source: str, db_session: Session = db_client):
    """
    Ссылка для скачивания таблицы
    :param request: запрос сессии
    :param source: название таблицы
    :param db_session: сессия БД
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")
    answer = IOService.download_table(source, db_session, request.session['created_ip'], request.session['id'])
    return answer
