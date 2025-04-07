from fastapi import APIRouter

admin_router = APIRouter(
    prefix="/admin",
    tags=["Администратору"],
)

@admin_router.post("/export")
async def export_database():
    """
    Экспортирование базы данных с сервера виде файла
    :return:
    """
    pass

@admin_router.post("/upload")
async def upload_database():
    """
    Импортирование базы данных на сервер как файл
    :return:
    """
    pass