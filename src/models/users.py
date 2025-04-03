import uuid

from sqlalchemy import Column, UUID, String, Integer

from src.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String, nullable=False)

    login: str = Column(String, nullable=True)
    hash_pass: str = Column(String, nullable=True)

    vkid: str = Column(String, nullable=True)
    rang: int = Column(Integer, nullable=False, default=5)

