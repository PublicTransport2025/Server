from typing import List

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from src.core.db import Base


class Stop(Base):
    __tablename__ = "stops"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False, unique=True)

    lat: float = Column(Float, nullable=False)
    lon: float = Column(Float, nullable=False)

    stage: int = Column(Integer, nullable=False, default=0)
    tpu_id: Mapped[int] = Column(ForeignKey("tpus.id", ondelete='SET NULL'), nullable=True)
    tpu: Mapped["Tpu"] = relationship(back_populates="stops")


class Tpu(Base):
    __tablename__ = "tpus"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False, unique=True)
    stops: Mapped[List["Stop"]] = relationship(back_populates="tpu")


