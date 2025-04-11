from typing import List, Optional

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Sequence, Boolean, Time, Date
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, relationship

from src.core.db import Base


class Atp(Base):
    __tablename__ = "atps"

    id: int = Column(Integer, Sequence('atps_seq'), primary_key=True)
    title: str = Column(String, nullable=False, unique=True)
    numbers: str = Column(String, nullable=False, unique=True)

    about: str = Column(String, nullable=True)
    phone: str = Column(String, nullable=True)
    report: str = Column(String, nullable=True)

    routes: Mapped[List["Route"]] = relationship(back_populates="atp", cascade='all, delete-orphan')


class Stop(Base):
    __tablename__ = "stops"

    id: int = Column(Integer, Sequence('stops_seq'), primary_key=True)
    name: str = Column(String, nullable=False)
    about: str = Column(String, nullable=True)

    lat: float = Column(Float, nullable=False)
    lon: float = Column(Float, nullable=False)

    stage: int = Column(Integer, nullable=False, default=0)
    tpu_id: Mapped[int] = Column(ForeignKey("tpus.id", ondelete="CASCADE"), nullable=True)
    tpu: Mapped["Tpu"] = relationship(back_populates="stops")
    sections: Mapped[List["Section"]] = relationship(back_populates="stop")


class Tpu(Base):
    __tablename__ = "tpus"

    id: int = Column(Integer, Sequence('tpus_seq'), primary_key=True)
    name: str = Column(String, nullable=False, unique=True)
    stops: Mapped[List["Stop"]] = relationship(back_populates="tpu", cascade='all, delete-orphan')


class Route(Base):
    __tablename__ = "routes"

    id: int = Column(Integer, Sequence('routes_seq'), primary_key=True)
    number: str = Column(String, nullable=False)
    label: str = Column(String, nullable=False)
    title: str = Column(String, nullable=False)

    info: str = Column(String, nullable=True)
    stage: int = Column(Integer, default=1)
    care: bool = Column(Boolean, default=False)

    atp_id: Mapped[Optional[int]] = Column(ForeignKey("atps.id", ondelete="CASCADE"), nullable=True)
    atp: Mapped["Atp"] = relationship(back_populates="routes")

    sections: Mapped[List["Section"]] = relationship(back_populates="route", cascade='all, delete-orphan')
    timetables: Mapped[List["Timetable"]] = relationship(back_populates="route", cascade='all, delete-orphan')
    traffics: Mapped[List["Traffic"]] = relationship(back_populates="route", cascade='all, delete-orphan')


class Section(Base):
    __tablename__ = "sections"

    route_id: Mapped[int] = Column(ForeignKey("routes.id", ondelete="CASCADE"), primary_key=True)
    order: int = Column(Integer, primary_key=True)

    stop_id: Mapped[int] = Column(ForeignKey("stops.id", ondelete="CASCADE"), nullable=False)
    coef: float = Column(Float, nullable=False)
    stage: int = Column(Integer, default=1)
    load: int = Column(Integer, default=0)

    stop: Mapped["Stop"] = relationship(back_populates="sections")
    route: Mapped["Route"] = relationship(back_populates="sections")

    chart_id: Mapped[int] = Column(ForeignKey("charts.id", ondelete="CASCADE"), nullable=True)
    chart: Mapped["Chart"] = relationship(back_populates="sections")


class Chart(Base):
    __tablename__ = "charts"

    id: int = Column(Integer, Sequence('charts_seq'), primary_key=True)
    label: str = Column(String, nullable=False)
    lats: List[float] = Column(ARRAY(Float), nullable=False)
    lons: List[float] = Column(ARRAY(Float), nullable=False)

    sections: Mapped[List["Section"]] = relationship(back_populates="chart", cascade='all, delete-orphan')


class Timetable(Base):
    __tablename__ = "timetables"

    id: int = Column(Integer, Sequence('timetables_seq'), primary_key=True)

    day = Column(Date, nullable=True)
    start = Column(Time, nullable=False)
    lap = Column(Time, nullable=False)

    route_id: Mapped[int] = Column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=True)
    route: Mapped["Route"] = relationship(back_populates="timetables")


class Traffic(Base):
    __tablename__ = "traffics"

    id: int = Column(Integer, Sequence('traffic_seq'), primary_key=True)

    day = Column(Date, nullable=True)
    start = Column(Time, nullable=False)
    end = Column(Time, nullable=False)
    lap = Column(Time, nullable=False)

    vehicles: int = Column(Integer, default=1)

    route_id: Mapped[int] = Column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=True)
    route: Mapped["Route"] = relationship(back_populates="traffics")
