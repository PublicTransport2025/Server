from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.models.users import Log, User

logs_router = APIRouter(
    prefix="/logs",
    tags=["Логи редакторов"],
)
templates = Jinja2Templates(directory="templates")


@logs_router.get('/{level}')
async def show_atps(request: Request, level: int, db_session: Session = db_client):
    """
    Отображает страницу логов редакции
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")

    logs = []
    rows = db_session.query(Log, User).join(User, User.id == Log.user_id).where(Log.level >= level).order_by(
        desc(Log.created_at)).limit(100).all()
    for row in rows:
        log, user = row
        logs.append({'name': user.name, 'vkid': user.vkid, 'action': log.action, 'information': log.information,
                     'created_ip': log.created_ip, 'created_at': log.created_at})
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})
