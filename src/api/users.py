from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.db import get_session
from src.models.users import User
from src.schemas.user import UserCreate, UserLogin, Token
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "1-2-3-4-5-6-7-8"  # Нужен ключ безопасности 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users_router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@users_router.post("/", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_session)):
    """
    Выполняет авторизацию пользователя
    """
    user = db.query(User).filter(User.login == login_data.email).first()
    if not user or not pwd_context.verify(login_data.password, user.hash_pass):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@users_router.post("/registration", response_model=Token)
async def registration(user_data: UserCreate, db: Session = Depends(get_session)):
    """
    Выполняет регистрацию пользователя
    """
    if db.query(User).filter(User.login == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user_data.password)
    new_user = User(name=user_data.name, login=user_data.email, hash_pass=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@users_router.patch("/")
async def change_password():
    """
    Изменяет пароль пользователя пользователя
    :return:
    """
    pass


@users_router.delete("/")
async def suspend():
    """
    Удаляет аккаунт пользователя
    :return:
    """
    pass