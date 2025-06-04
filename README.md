# Server
**Серверная часть** программного комплекса обеспечивает *актуальность данных* и *высокую скорость* работы системы при предоставлении данных о *работе транспорта* и *построении оптимальных маршрутов*.

🌐 **Веб-сайт проекта**: [transport3ka.ru](https://transport3ka.ru/)

## Модель предсказания
Система использует современные методы машинного обучения для прогнозирования пассажиропотока на маршрутах общественного транспорта. Наша модель обучалась на данных, полученных официально от Управления транспорта ([смотреть документ](https://github.com/PublicTransport2025/Docs/blob/main/%D0%94%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B%20%D0%B8%20%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D1%8F/%D0%97%D0%B0%D0%BF%D1%80%D0%BE%D1%81%20%D0%B2%20%D1%83%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%20%D1%82%D1%80%D0%B0%D0%BD%D1%81%D0%BF%D0%BE%D1%80%D1%82%D0%B0.pdf))

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
1. Загрузите проект на свой компьютер ```git clone https://github.com/PublicTransport2025/Server.git <папка> ```
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
WEB_CLIENT_SECRET=Данные о приложениях ВК из кабинета разработчика
WEB_REDIRECT_URI=http://localhost/web/profile/auth


MOBILE_CLIENT_ID=Данные о приложениях ВК из кабинета разработчика
MOBILE_CLIENT_SECRET=Данные о приложениях ВК из кабинета разработчика
MOBILE_REDIRECT_URI=vk1234://vk.com/blank.html

ADMIN_VK=VKID администратора, который будет создан в БД (только цифры)

JWT_SECRET_KEY=Произвольная текстовая строка
JWT_ALGORITHM=HS256 #алгоритм для jwt
ACCESS_TOKEN_EXPIRE_MINUTES=15 #время жизни access токена
REFRESH_TOKEN_EXPIRE_DAYS=90  #время жизни refresh токена

ADMIN_EMAIL=Почта администратора, который будет создан в БД
ADMIN_PASSWORD=Пароль администратора, который будет создан в БД

MAP_KEY=94387bd6-9244-4294-93d9-3d333dd50f08

SMTP_USER=Почта для отправки кода
SMTP_PASSWORD=Пароль почты(нужен из раздела безопасности)

```
7. Инициализируйте базу данных ```poetry run alembic upgrade head```
8. Запустите проект через ```poetry run python -m src.main```
9. Авторизируйтесь через ВК и импортируйте таблицы в базу данных
10. Проверить функционал API можно по ссылке ```http://localhost/docs```


## Запуск модели предсказания
Инференс модели реализован как сервис внутри проекта.  
📁 Папка с файлами модели находится в корне репозитория: [model_ml](https://github.com/PublicTransport2025/Server/tree/main/model_ml)

Файлы, необходимые для запуска модели:  
- `xgboost_model.pkl`  
- `target_encoder.pkl`  
- `unique_route_ids.pkl`  
- `passenger_avg_by_route_hour.pkl`  

Пример класса для использования нашей модели:
```python
import logging
import traceback
from pathlib import Path
from typing import Union

import joblib
import pandas as pd
from fastapi import HTTPException


MODEL_DIR = Path("model_ml")

try:
    xgb_model = joblib.load(MODEL_DIR / "xgboost_model.pkl")
    encoder = joblib.load(MODEL_DIR / "target_encoder.pkl")
    known_route_ids = joblib.load(MODEL_DIR / "unique_route_ids.pkl")
    avg_passengers_stats = joblib.load(MODEL_DIR / "passenger_avg_by_route_hour.pkl")
except Exception as exc:
    msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logging.error(f"Ошибка при загрузке модели: \n{msg}")
    raise

class MlService:
    @staticmethod
    def get_day_part(hour: int) -> str:
        if 5 <= hour < 10: return 'утро'
        elif 10 <= hour < 17: return 'день'
        elif 17 <= hour < 22: return 'вечер'
        else: return 'ночь'

    @staticmethod
    def predict_passengers(data: dict) -> Union[float, str]:
        """
        Принимает на вход JSON-словарь с параметрами поездки:
        {
          "route_id": id,
          "order": 1,
          "stop_id": id,
          "Время": "06:42:00",
          "День недели": "Пятница"
        }
        """

        try:
            route_id = data["route_id"]
            stop_id = data["stop_id"]

            if route_id not in known_route_ids:
                return f"route_id {route_id} не обучен в модели"

            time = pd.to_datetime(data["Время"], format="%H:%M:%S")
            hour = time.hour
            minute = time.minute
            time_minutes = hour * 60 + minute
            day_part = MlService.get_day_part(hour)
            avg_val = avg_passengers_stats.get((route_id, hour), 0)

            features = {
                "route_id": route_id,
                "order": data["order"],
                "stop_id": stop_id,
                "День недели": data["День недели"],
                "hour": hour,
                "minute": minute,
                "time_minutes": time_minutes,
                "day_part": day_part,
                "route_stop": f"{route_id}_{stop_id}",
                "avg_passengers_route_hour": avg_val
            }

            df = pd.DataFrame([features])

            column_order = [
                "route_id", "order", "stop_id", "День недели", "hour",
                "minute", "time_minutes", "day_part", "route_stop", "avg_passengers_route_hour"
            ]

            df = df[column_order]
            df_encoded = encoder.transform(df)

            prediction = xgb_model.predict(df_encoded)[0]

            return round(float(prediction), 2)

        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, detail="Ошибка обработки модели")
```

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
