from pydantic import BaseModel

class PredictionInput(BaseModel):
    route_id: int
    order: int
    stop_id: int
    time: str
    day_of_week: str