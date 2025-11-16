from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, Interval, String

from main import Base


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True, default=datetime.utcnow)
    duration = Column(Interval)
    description = Column(String, index=True)
    comments = Column(String, nullable=True)
    distractions = Column(Integer, default=0)


class SetBase(BaseModel):
    date: Optional[datetime] = None
    description: str
    duration: timedelta
    comments: Optional[str] = None
    distractions: Optional[int] = 0


class SetResponse(SetBase):
    id: int

    class Config:
        from_attributes = True


class SetGroupedResponse(BaseModel):
    description: str
    count: int

    class Config:
        from_attributes = True
