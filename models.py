from sqlalchemy import Column, String, Integer, DateTime, Boolean
from database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    short_code = Column(String, unique=True, index=True)
    original_url = Column(String)
    clicks = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    is_reachable= Column(Boolean, default=True)