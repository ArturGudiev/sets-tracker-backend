from typing import Optional
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv

from models import Base, BigSet, Set
from schemas import BigSetResponse, SetGroupedResponse, SetResponse, SetBase

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/mine"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="SetsTrack",
    description=description,
    summary="Do you stuff. Set your tracks and track your sets.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:8001"    
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/sets/", response_model=list[SetResponse])
async def read_items(date: Optional[datetime] = None, db: Session = Depends(get_db)):
    query = db.query(Set)
    if date:
        query = query.filter(Set.date == date)
    sets = query.all()
    return sets


@app.get("/sets/today", response_model=list[SetResponse])
async def read_items(db: Session = Depends(get_db)):    
    sets = db.query(Set).filter(func.date(Set.date) == datetime.now().date()).all()
    return sets


@app.get("/sets/today-grouped", response_model=list[SetGroupedResponse])
async def read_items(db: Session = Depends(get_db)):    
    results = db.query(Set.description, func.count(Set.id).label('count')).filter(func.date(
        Set.date) == datetime.now().date()).group_by(Set.description).all()
    return [SetGroupedResponse(description=desc, count=count) for desc, count in results]
    
@app.get("/big-sets/", response_model=list[BigSetResponse])
async def read_items(db: Session = Depends(get_db)):    
    results = db.query(BigSet.id, BigSet.description).all()
    return [BigSetResponse(id=obj.id, description=obj.description, created=obj.created, finished=obj.finished) for obj in results]
    


@app.get("/sets/{set_id}", response_model=SetResponse)
async def read_item(set_id: int, db: Session = Depends(get_db)):
    set = db.query(Set).filter(Set.id == set_id).first()
    if set is None:
        return {"error": "Set not found"}
    return set

@app.post("/set/create", response_model=SetResponse)
async def add_set(set: SetBase, db: Session = Depends(get_db)):
    # Create a new Set instance from the Pydantic model
    db_set = Set(
        date=set.date,
        duration=set.duration,
        description=set.description,
        comments=set.comments,
        distractions=set.distractions
    )
    # Add the new set to the database
    db.add(db_set)
    db.commit()
    db.refresh(db_set)  # Refresh to get the generated ID
    print(db_set)
    print('after adding a set')
    return db_set

# @app.post("/items/")
# async def create_item(name: str, description: str = None, db: Session = Depends(get_db)):
#     item = Item(name=name, description=description)
#     db.add(item)
#     db.commit()
#     db.refresh(item)
#     return item

# @app.get("/health")
# async def health_check(db: Session = Depends(get_db)):
#     """Test database connection"""
#     try:
#         # Try to query the database
#         db.execute("SELECT 1")
#         return {"status": "healthy", "database": "connected"}
#     except Exception as e:
#         return {"status": "unhealthy", "database": "disconnected", "error": str(e)}