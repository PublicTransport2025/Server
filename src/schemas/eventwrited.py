from pydantic import BaseModel


class EventWrited(BaseModel):
    type: int
    line: int
    lat: float
    lon: float
