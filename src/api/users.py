from fastapi import APIRouter

users_router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@users_router.post("/")
async def login():
    """
    Выполняет авторизацию пользователя
    :return:
    """
    pass

@users_router.post("/registration")
async def registration():
    """
    Выполняет регистрацию пользователя
    :return:
    """
    pass

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