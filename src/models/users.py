import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, UUID, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, relationship

from src.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String, nullable=False)

    login: str = Column(String, nullable=True, unique=True, index=True)
    hash_pass = Column(String, nullable=True)


    vkid: str = Column(String, nullable=True)

    rang: int = Column(Integer, nullable=False, default=5)

    logs: Mapped[List["Log"]] = relationship(back_populates="user")


class Log(Base):
    __tablename__ = "logs"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    created_ip: str = Column(String(15), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now)

    level: str = Column(Integer, nullable=False)
    action: str = Column(String, nullable=False)
    information: str = Column(Text, nullable=True)

    user_id: Mapped[UUID] = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="logs")
