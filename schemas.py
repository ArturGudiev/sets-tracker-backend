from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel as _BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class BaseModel(_BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class SetGroupedResponse(BaseModel):
    description: str
    count: int

    class Config:
        from_attributes = True


class SetBase(BaseModel):
    date: Optional[datetime] = None
    description: str
    duration: Optional[timedelta] = None
    comments: Optional[str] = None
    distractions: Optional[int] = 0



class BigSetResponse(BaseModel):
    id: int
    description: str
    created: datetime
    finished: Optional[datetime]



class SetResponse(SetBase):
    id: int

    class Config:
        from_attributes = True
