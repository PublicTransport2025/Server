from typing import Optional

from pydantic import BaseModel

from src.schemas.coord import Coord


class StopModel(BaseModel):
    id: int
    name: str
    about: Optional[str]
    coord: Coord


class StopInput(BaseModel):
    name: str
    about: str
    lat: float
    lon: float
    stage: int
    tpu_id: Optional[int] = None


class StopUpd(StopInput):
    id: int
