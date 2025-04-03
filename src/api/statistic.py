from fastapi import APIRouter

statistic_router = APIRouter(
    prefix="/statistic",
    tags=["Статистика"],
)

@statistic_router.post("/setup")
async def report_setup():
    """
    Отправка статистики об установке приложения
    :return:
    """
    pass


@statistic_router.post("/created")
async def report_created():
    """
    Отправка статистики о построении маршрута
    :return:
    """
    pass

@statistic_router.post("/scoring")
async def scoring_route():
    """
    Отправка оценки построенного маршрута
    :return:
    """
    pass