import logging
import traceback

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.core.db import db_client
from src.models.users import User, Log
from src.utils.security import hash_password

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
    rows = db_session.query(User).order_by(User.name).all()
    for admin in rows:
        if admin.rang == 99:
            rang = 'Руководитель'
        elif admin.rang >= 50:
            rang = 'Администратор'
        elif admin.rang >= 5:
            rang = 'Пользователь'
        else:
            rang = 'Заблокирован'
        admins.append({'name': admin.name, 'login': admin.login, 'vkid': admin.vkid, 'rang': rang, 'id': admin.id})
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
              action='Разжаловал редактора | Разблокировал пользователя',
              information="vk.com/id" + str(user.vkid),
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
              information="vk.com/id" + str(user.vkid),
              user_id=request.session["id"])
    db_session.add(log)
    db_session.commit()
    return RedirectResponse("/web/admins", status_code=303)


@admins_router.post('/banform')
async def banform(request: Request, db_session: Session = db_client):
    """
    Блокирует пользователя
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    form_data = await request.form()
    user_id = form_data.get("admin")

    user = db_session.query(User).filter(User.id == user_id).one()
    user.rang = 2
    log = Log(created_ip=request.session["created_ip"],
              level=10,
              action='Заблокировал пользователя',
              information=str(user_id),
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

    try:
        form_data = await request.form()

        name = form_data.get('name')
        vkid = form_data.get('vkid')
        login = form_data.get('login_input')
        password = form_data.get('password_input')

        if not vkid.isdecimal():
            vkid = None

        if login == '' or password == '':
            login = None
            password = None
        else:
            password = hash_password(password)

        if not vkid and not login:
            raise HTTPException(500, "Укажите хотя бы один способ авторизации")

        user = User(name=name, vkid=vkid, login=login, hash_pass=password)
        log = Log(created_ip=request.session["created_ip"],
                  level=5,
                  action='Создал профиль сотрудника',
                  information=name + " vk.com/id" + str(vkid),
                  user_id=request.session["id"])
        db_session.add(log)
        db_session.add(user)
        db_session.commit()

        db_session.commit()
        return RedirectResponse("/web/admins", status_code=303)
    except Exception as exc:
        msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logging.error(msg)
        raise HTTPException(500, str(exc))


@admins_router.delete('/ban/{id}')
async def ban(request: Request, id: str, db_session: Session = db_client):
    """
    Обрабатывает запрос блокировки пользователя
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login", status_code=303)

    user = db_session.query(User).filter(User.id == id).one()
    user.rang = 2
    log = Log(created_ip=request.session["created_ip"],
              level=3,
              action='Заблокировал пользователя',
              information=str(id),
              user_id=request.session["id"])
    db_session.add(log)
    db_session.commit()

    return JSONResponse(content={"message": "Пользователь заблокирован"}, status_code=200)
