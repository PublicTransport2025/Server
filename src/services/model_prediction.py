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
    
    @staticmethod  
    def calculate_load_level(passengers: float) -> int:
        if passengers <= 3:
            return 0
        elif passengers <= 6:
            return 1
        elif passengers <= 9:
            return 2
        elif passengers <= 12:
            return 3
        elif passengers <= 15:
            return 4
        else:
            return 5