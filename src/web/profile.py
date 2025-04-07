import base64
import hashlib
import random
import string
from uuid import uuid4

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from src.core.constants import WEB_CLIENT_ID, WEB_REDIRECT_URI
from src.core.db import db_client
from src.models.users import User
from src.utils.users import decode_vk_id

profile_router = APIRouter(
    prefix="/profile",
    tags=["Профиль"],
)
templates = Jinja2Templates(directory="templates")


@profile_router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """
    Отображает страницу авторизации, настраивая ПКСЕ-параметры для авторизации через ВК
    :return:
    """
    client_id = WEB_CLIENT_ID
    redirect_uri = WEB_REDIRECT_URI

    state = str(uuid4())
    request.session["state"] = state

    characters = string.ascii_letters + string.digits + '_-'
    code_verifier = ''.join(random.choice(characters) for _ in range(random.randint(43, 128)))
    request.session["code_verifier"] = code_verifier

    s256_digester = hashlib.sha256()
    input_bytes = code_verifier.encode('iso-8859-1')
    s256_digester.update(input_bytes)
    digest_bytes = s256_digester.digest()
    code_challenge = base64.urlsafe_b64encode(digest_bytes).decode('utf-8').rstrip('=')

    return templates.TemplateResponse("login.html", {"request": request, "redirect_uri": redirect_uri,
                                                     "client_id": client_id, "state": state,
                                                     "code_challenge": code_challenge})


@profile_router.get('/auth')
async def auth(request: Request, code: str, state: str, device_id: str, db_session=db_client):
    """
    Обработчик авторизации через ВК
    :param request:
    :param code:
    :param state:
    :param device_id:
    :param db_session:
    :return:
    """
    if request.session['state'] != state:
        raise HTTPException(400, "Security error")
    vkid = await decode_vk_id(request.session["code_verifier"], code, device_id, state, True)
    vkid = str(vkid)
    user = db_session.query(User).filter(User.vkid == vkid).filter(User.rang >= 50).one_or_none()
    if user is None:
        raise HTTPException(403, "Haven't permissions")
    request.session['id'] = str(user.id)
    request.session['name'] = user.name
    request.session['rang'] = user.rang
    return RedirectResponse("/web/profile")


@profile_router.get('')
async def profile(request: Request):
    """
    Отображает страницу личного кабинета администратора
    :param request:
    :return:
    """
    if not request.session.keys().__contains__('id') or request.session['rang'] < 50:
        return RedirectResponse("/web/profile/login")
    name = request.session['name']
    return templates.TemplateResponse("profile.html", {"request": request, "name": name})
