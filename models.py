from sqlalchemy import Column, String, Integer, DateTime
from database import Base
from datetime import datetime, timezone

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    short_code = Column(String, unique=True, index=True)
    original_url = Column(String)
    clicks = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)