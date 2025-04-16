from typing import List

from pydantic import BaseModel

from src.schemas.coord import Coord


class RouteSimple(BaseModel):
    label: str
    number: str
    long: str
    load: int
    stops: List[Coord]


class RouteReport(BaseModel):
    result: int
    count: int
    simple_routes: List[RouteSimple]
