from fastapi import APIRouter, HTTPException
from src.schemas.prediction import PredictionInput
from src.services.model_prediction import MlService
from typing import Union

predict_router = APIRouter(
    prefix="/predict",
    tags=["Предсказание модели"],
)


@predict_router.post("/", summary="Предсказание загруженности автобуса")
def predict_passenger_count(request: PredictionInput) -> dict:
    """
    Возвращает предсказанное число пассажиров на остановке
    и оценивает загруженность автобуса по шкале [0–5].

    Если order > 0, также учитывает вход с предыдущей остановки.

    ---
    Пример запроса:
    {
      "route_id": 163,
      "order": 3,
      "stop_id": 281,
      "time": "07:30:00",
      "day_of_week": "Пятница"
    }
    """
    current_input = {
        "route_id": request.route_id,
        "order": request.order,
        "stop_id": request.stop_id,
        "Время": request.time,
        "День недели": request.day_of_week
    }

    current_pred = MlService.predict_passengers(current_input)

    if not isinstance(current_pred, (float, int)):
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка предсказания на текущей остановке: {current_pred}"
        )

    total_passengers = current_pred

    if request.order > 0:
        previous_input = current_input.copy()
        previous_input["order"] = request.order - 1

        previous_pred = MlService.predict_passengers(previous_input)

        if isinstance(previous_pred, (float, int)):
            total_passengers += previous_pred

    load_level = MlService.calculate_load_level(total_passengers)

    return {
        "predicted_passengers_current": current_pred,
        "accumulated_passengers": round(total_passengers, 2),
        "load_level_0_5": load_level
    }