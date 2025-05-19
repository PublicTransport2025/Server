from typing import List

from pydantic import BaseModel

from src.schemas.coord import Coord


class RouteSimple(BaseModel):
    label: str
    number: str
    load: int
    time_label: str
    time_begin: str
    time_road: str
    stops: List[Coord]


class RouteDouble(BaseModel):
    label1: str
    number1: str
    load1: int
    time_label1: str
    time_begin1: str
    time_road1: str
    stop1: str
    stops1: List[Coord]

    label2: str
    number2: str
    load2: int
    time_label2: str
    time_begin2: str
    time_road2: str
    stop2: str
    stops2: List[Coord]



class RouteReport(BaseModel):
    result: int
    count: int
    count_simple: int
    simple_routes: List[RouteSimple]
    double_routes: List[RouteDouble]
