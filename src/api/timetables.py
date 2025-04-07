from fastapi import APIRouter


timetables_router = APIRouter(
    prefix="/timetables",
    tags=["Расписания"],
)

@timetables_router.get("/")
async def get_timetable():
    """
    Передает расписание для заданного маршрута
    :return:
    """
    pass