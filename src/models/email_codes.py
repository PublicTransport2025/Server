import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from src.core.db import Base

class EmailCode(Base):
    __tablename__ = "email_codes"

    email = Column(String, primary_key=True)
    code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)