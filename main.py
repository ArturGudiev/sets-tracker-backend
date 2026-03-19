from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv

from models import Base, BigSet, Set
from schemas import BigSetResponse, SetGroupedResponse, SetResponse, SetBase, BigSetCreate, BigSetFull, \
    AddSetToBigSetRequest

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

# Add CORS middleware (fully open during development)
app.add_middleware( # TODO fix later
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
async def read_big_sets(db: Session = Depends(get_db)):
    """
    Получение всех BigSet
    """
    results = db.query(BigSet.id, BigSet.description, BigSet.created, BigSet.finished).all()
    return [BigSetResponse(id=obj.id, description=obj.description, created=obj.created, finished=obj.finished) for obj in results]


@app.get("/big-sets/{big_set_id}", response_model=BigSetFull)
async def read_big_sets(big_set_id: int, db: Session = Depends(get_db)):
    """
    Получение всех BigSet
    """
    big_set = db.query(BigSet).filter(BigSet.id == big_set_id).first()
    sets = db.query(Set).filter(Set.big_set_id == big_set_id).all()
    return BigSetFull(
        id=big_set.id,
        description=big_set.description,
        created=big_set.created,
        finished=big_set.finished,
        sets=sets)


@app.post("/big-sets/{big_set_id}/sets", response_model=BigSetFull)
async def read_big_sets(big_set_id: int, append_set_request: AddSetToBigSetRequest, db: Session = Depends(get_db)):
    """
    Получение всех BigSet
    """
    sets = db.query(Set).filter(Set.big_set_id == big_set_id).all()

    new_set = Set(
        date=datetime.now(),
        duration=None,
        description=append_set_request.description,
        comments="",
        distractions=0,
        big_set_id=big_set_id,
    )
    db.add(new_set)
    db.commit()

    big_set = db.query(BigSet).filter(BigSet.id == big_set_id).first()
    sets = db.query(Set).filter(Set.big_set_id == big_set_id).all()
    return BigSetFull(
        id=big_set.id,
        description=big_set.description,
        created=big_set.created,
        finished=big_set.finished,
        sets=sets)


@app.post("/big-sets/create", response_model=BigSetFull)
async def create_big_set(big_set_create_request: BigSetCreate, db: Session = Depends(get_db)):
    """
    Создание нового BigSet
    """
    db_big_set = BigSet(
        description=big_set_create_request.description,
        created = big_set_create_request.created
    )
    db.add(db_big_set)
    db.commit()
    db.refresh(db_big_set)  # Refresh to get the generated ID

    # create related Set records
    number_of_sets = big_set_create_request.number_of_sets
    created_sets: list[Set] = []

    for _ in range(number_of_sets):
        new_set = Set(
            date=datetime.now(),
            duration=None,
            description=big_set_create_request.description,
            comments="",
            distractions=0,
            big_set_id=db_big_set.id,
        )
        db.add(new_set)
        created_sets.append(new_set)

    db.commit()

    # ensure all created sets are refreshed (ids populated)
    for s in created_sets:
        db.refresh(s)

    return BigSetFull(
        id=db_big_set.id,
        description=db_big_set.description,
        created=db_big_set.created,
        finished=db_big_set.finished,
        sets=[
            SetResponse(
                id=s.id,
                date=s.date,
                description=s.description,
                duration=s.duration,
                comments=s.comments,
                distractions=s.distractions,
            )
            for s in created_sets
        ],
    )



@app.get("/sets/{set_id}", response_model=SetResponse)
async def read_set(set_id: int, db: Session = Depends(get_db)):
    set = db.query(Set).filter(Set.id == set_id).first()
    if set is None:
        return {"error": "Set not found"}
    return set


@app.put("/sets/{set_id}", response_model=SetResponse)
async def update_set(set_id: int, set_request: SetBase, db: Session = Depends(get_db)):
    set = db.query(Set).filter(Set.id == set_id).first()
    set.description = set_request.description
    set.comments = set_request.comments
    set.duration = set_request.duration
    set.distractions = set_request.distractions
    db_set = Set(
        id=set_id,
        date=set.date,
        duration=set.duration,
        description=set.description,
        comments=set.comments,
        distractions=set.distractions
    )
    db.add(db_set)
    db.commit()
    db.refresh(db_set)  # Refresh to get the generated ID
    print(db_set)
    print('after adding a set')
    return db_set


@app.delete("/sets/{set_id}", response_model=SetResponse)
async def delete_set(set_id: int, db: Session = Depends(get_db)):
    set_to_delete = db.query(Set).filter(Set.id == set_id).first()
    db.delete(set_to_delete)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Set was deleted"}
    )


@app.put("/set/{set_id}", response_model=SetResponse)
async def add_set(set: SetBase, set_id: int, db: Session = Depends(get_db)):
    db_set = db.query(Set).filter(Set.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    db_set.date = set.date
    db_set.duration = set.duration
    db_set.description = set.description
    db_set.comments = set.comments
    db_set.distractions = set.distractions
    db.commit()
    db.refresh(db_set)
    return db_set

