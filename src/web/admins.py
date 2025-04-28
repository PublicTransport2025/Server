from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.models.users import User, Log

admins_router = APIRouter(
    prefix="/admins",
    tags=["Редакция"],
)
templates = Jinja2Templates(directory="templates")


@admins_router.get('')
async def show_admins(request: Request, db_session: Session = db_client):
    """
    Отображает страницу со списком администрации
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    admins = []
    rows = db_session.query(User).all()
    for admin in rows:
        if admin.rang == 99:
            rang = 'Руководитель'
        elif admin.rang >= 50:
            rang = 'Администратор'
        else:
            rang = 'Пользователь'
        admins.append({'name': admin.name, 'vkid': admin.vkid, 'rang': rang, 'id': admin.id})
    return templates.TemplateResponse("admins.html", {"request": request, "admins": admins})


@admins_router.post('/reset')
async def reset_admin(request: Request, db_session: Session = db_client):
    """
    Сбрасывает должность администратора
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    form_data = await request.form()
    user_id = form_data.get("admin")

    user = db_session.query(User).filter(User.id == user_id).one()
    user.rang = 5
    log = Log(created_ip=request.session["created_ip"],
              level=10,
              action='Разжаловал редактора',
              information="vk.com/id"+str(user.vkid),
              user_id=request.session["id"])
    db_session.add(log)
    db_session.commit()
    return RedirectResponse("/web/admins", status_code=303)


@admins_router.post('/setup')
async def setup_admin(request: Request, db_session: Session = db_client):
    """
    Назначает ранг администратора
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    form_data = await request.form()
    user_id = form_data.get("admin")

    user = db_session.query(User).filter(User.id == user_id).one()
    user.rang = 55
    log = Log(created_ip=request.session["created_ip"],
              level=10,
              action='Назначил редактора',
              information="vk.com/id"+str(user.vkid),
              user_id=request.session["id"])
    db_session.add(log)
    db_session.commit()
    return RedirectResponse("/web/admins", status_code=303)


@admins_router.post('/add')
async def add_admin(request: Request, db_session: Session = db_client):
    """
    Обрабатывает форму создания нового сотрудника
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    form_data = await request.form()

    name = form_data.get('name')
    vkid = form_data.get('vkid')

    user = User(name=name, vkid=vkid)
    log = Log(created_ip=request.session["created_ip"],
              level=5,
              action='Создал профиль сотрудника',
              information=name+" vk.com/id"+str(vkid),
              user_id=request.session["id"])
    db_session.add(log)
    db_session.add(user)
    db_session.commit()

    db_session.commit()
    return RedirectResponse("/web/admins", status_code=303)
