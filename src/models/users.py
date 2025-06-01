import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, UUID, String, Integer, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, relationship

from src.core.db import Base


class UserStopLikes(Base):
    __tablename__ = "user_stop"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    stop_id = Column(Integer, ForeignKey("stops.id", ondelete="CASCADE"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String, nullable=False)
    login: str = Column(String, nullable=True, unique=True, index=True)
    hash_pass = Column(String, nullable=True)
    vkid: str = Column(String, nullable=True, unique=True, index=True)
    rang: int = Column(Integer, nullable=False, default=5)
    logs: Mapped[List["Log"]] = relationship(back_populates="user_log")
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="user_feedback")
    events: Mapped[List["Event"]] = relationship(back_populates="user_event")


class Log(Base):
    __tablename__ = "logs"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_ip: str = Column(String(15), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now)
    level: str = Column(Integer, nullable=False)
    action: str = Column(String, nullable=False)
    information: str = Column(Text, nullable=True)
    user_id: Mapped[UUID] = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    user_log: Mapped["User"] = relationship(back_populates="logs")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    mark: str = Column(Integer, nullable=False)
    about: str = Column(Text, nullable=True)

    answered: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.now)

    user_id: Mapped[UUID] = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    user_feedback: Mapped["User"] = relationship(back_populates="feedbacks")


class Event(Base):
    __tablename__ = "events"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    type: float = Column(Integer, nullable=False)
    line: float = Column(Integer, nullable=False)
    lat: float = Column(Float, nullable=False)
    lon: float = Column(Float, nullable=False)

    moderated: bool = Column(Integer, default=0)
    created_at: datetime = Column(DateTime, default=datetime.now)

    user_id: Mapped[UUID] = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    user_event: Mapped["User"] = relationship(back_populates="events")
