from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.core.db import get_session
from src.models.users import User
from passlib.context import CryptContext

templates = Jinja2Templates(directory="templates")
auth_router = APIRouter(prefix="/web")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@auth_router.get("/login")
async def login_page(request: Request):
    """Отображает страницу входа"""
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_session)):
    """Обрабатывает вход через email и пароль"""
    user = db.query(User).filter(User.login == email).first()
    if user and pwd_context.verify(password, user.hash_pass):
        request.session["user_id"] = str(user.id)
        request.session["name"] = user.name
        request.session["rang"] = user.rang
        return RedirectResponse(url="/web/profile", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный email или пароль"})