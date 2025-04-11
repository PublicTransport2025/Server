# Server
**Серверная часть** программного комплекса обеспечивает *актуальность данных* и *высокую скорость* работы системы при предоставлении данных о *работе транспорта* и *построении оптимальных маршрутов*.

## Стек технологий

<table align="center" width='100%'>
<tr><td>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Python 3.12 - Основной язык разработки
</td><td>

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

Асинхронный WEB-фреймворк для Python
</td><td>

![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

Высокопроизводительная база данных
</td></tr><table>

## Установка и локальный запуск
1. Загрузите проект на свой компьютер ```git glone https://github.com/PublicTransport2025/Server.git <папка> ```
2. Перейдите в скаченную папку ```cd <папка> ```
3. Установите виртуальную среду poetry и систему контроля версий базы данных ```pip install poetry alembic```
4. Установите необхоимые python библиотеки ```poetry install --no-root```
5. Установите базу данных PostgreSQL с официального сайта как самостоятельное приложение или используя пустой Docker-образ
6. Создайте файл .env и заполните его следующим образом
```
LOCALHOST=localhost
PORT=80

VERSION=DEBUG
API_KEY=Произвольная текстовая строка

DB_NAME=Название базы данных
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres

WEB_CLIENT_ID=Данные о приложениях ВК из кабинета разработчика
WEB_CLIENT_SECRET=
WEB_REDIRECT_URI=http://localhost/web/profile/auth

MOBILE_CLIENT_ID=
MOBILE_CLIENT_SECRET=
MOBILE_REDIRECT_URI=vk1234://vk.com/blank.html

ADMIN_VK=VKID администратора, который будет создан в БД (только цифры)
```
7. Инициализируйте базу данных ```alembic upgrade head```
8. Запустите проект через ```poetry run python -m src.main```
9. Авторизируйтесь через ВК и импортируйте таблицы в базу данных
10. Проверить функционал API можно по ссылке ```http://localhost/docs```

## Код-стайл
1. Технические требования:
   * Версия Python 3.12
   * Система контроля версий Poetry
   * ORM обязателен при работе с базой данных
   * Ошибки обрабатываются и логируются на уровне сервисов
2. Оформление кода:
   * Названия функций и переменных ```snake_case```, классов ```CamelCase```, констант ```UPPER_CASE```
   * Размер табуляции - 4 пробела
   * Каждой функции соответствует документация
   * Комментарии оформляются на русском языке
   * Логика максимально декомпозируется на отдельные функции
3. Оформление коммитов:
   * Формат коммита task-number: description
   * Коммиты оформляются на английском языке
   * Номер и тип задач должны соответствовать таск-трекеру
   * Названия веток: ```main``` ```release``` ```dev``` ```feature``` ```fix``` 
