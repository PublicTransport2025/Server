from fastapi import APIRouter

operator_router = APIRouter(
    prefix="/operator",
    tags=["Диспетчеру"],
)

@operator_router.get("/vehicle")
async def get_vehicle():
    """
    Выводит выпуск по всем маршрутам
    :return:
    """
    pass

@operator_router.patch("/vehicle")
async def update_vehicle():
    """
    Уточняет выпуск на маршруте
    :return:
    """
    pass


@operator_router.get("/timetable")
async def get_timetable():
    """
    Выводит асписание маршрута
    :return:
    """
    pass

@operator_router.put("/timetable")
async def edit_timetable():
    """
    Редактирует расписание маршрута
    :return:
    """
    pass