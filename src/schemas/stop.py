from typing import List

from pydantic import BaseModel

from src.schemas.coord import Coord


class StopSchema(BaseModel):
    id: int
    name: str
    coord: Coord
