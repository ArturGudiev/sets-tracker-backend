from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Interval, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True, default=datetime.utcnow)
    duration = Column(Interval)
    description = Column(String, index=True)
    comments = Column(String, nullable=True)
    distractions = Column(Integer, default=0)


class BigSet(Base):
    __tablename__ = "big_sets"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    created = Column(DateTime, index=True, default=datetime.utcnow)
    finished = Column(DateTime, index=True, default=datetime.utcnow)


