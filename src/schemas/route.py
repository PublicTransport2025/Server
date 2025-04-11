from typing import List, Optional

from pydantic import BaseModel

from src.schemas.coord import Coord


class Route(BaseModel):
    stops: List[Coord]


class RouteInput(BaseModel):
    number: str
    label: str
    title: str
    info: Optional[str] = None
    stage: int
    care: bool
    atp_id: Optional[int] = None


class RouteModel(RouteInput):
    id: int


class SectionModel(BaseModel):
    stop_id: int
    coef: float
    load: int
    chart_id: int


class SectionsInput(BaseModel):
    sections: List[SectionModel]
