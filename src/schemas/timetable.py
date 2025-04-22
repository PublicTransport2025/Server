from pydantic import BaseModel


class TimetableInput(BaseModel):
    start: str
    lap: str
    route_id: int


class TimetableModel(TimetableInput):
    id: int
