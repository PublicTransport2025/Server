from typing import List

from pydantic import BaseModel

from src.schemas.coord import Coord


class Route(BaseModel):
    stops: List[Coord]
