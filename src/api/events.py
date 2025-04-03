from fastapi import APIRouter

events_router = APIRouter(
    prefix="/events",
    tags=["События"],
)


@events_router.get("/")
async def get_events():
    """
    Передает все дорожные события
    :return:
    """
    pass


@events_router.post("/")
async def add_event():
    """
    Добавляет дорожное событие
    :return:
    """
    pass

@events_router.put("/")
async def setup_event():
    """
    Редактирует собственное дорожное событие
    :return:
    """
    pass

@events_router.delete("/")
async def delete_event():
    """
    Удаляет собственное дорожное событие
    :return:
    """
    pass

@events_router.post("/check")
async def check_event():
    """
    Подтверждает или опровергает чужое дорожное событие
    :return:
    """
    pass

