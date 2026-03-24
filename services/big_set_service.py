# app/services/user_service.py
from fastapi import Depends
from sqlalchemy.orm import Session

from main import get_db
from models import Set, BigSet
from schemas import BigSetFull


class BigSetService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_big_set_full(self, big_set_id: int) -> BigSetFull:
        """
        Get big set by id
        """
        big_set = self.db.query(BigSet).filter(BigSet.id == big_set_id).first()
        sets = self.db.query(Set).filter(Set.big_set_id == big_set_id).all()
        return BigSetFull(
            id=big_set.id,
            description=big_set.description,
            created=big_set.created,
            finished=big_set.finished,
            sets=sets)
