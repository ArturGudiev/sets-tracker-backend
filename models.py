from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Interval, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    duration = Column(Interval)
    description = Column(String, index=True)
    comments = Column(String, nullable=True)
    distractions = Column(Integer, default=0)
    big_set_id = Column(Integer, ForeignKey("big_sets.id"), nullable=True, index=True)


class BigSet(Base):
    __tablename__ = "big_sets"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    created = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    finished = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))


