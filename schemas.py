from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel as _BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(_BaseModel):
    """
    Snake_case attributes in Python, no aliasing.
    """

    model_config = ConfigDict(from_attributes=True)


class CamelModel(BaseModel):
    """
    Snake_case in Python, camelCase in JSON (I/O).
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class SetGroupedResponse(CamelModel):
    description: str
    count: int


class SetBase(CamelModel):
    date: Optional[datetime] = None
    description: str
    duration: Optional[timedelta] = None
    comments: Optional[str] = None
    distractions: Optional[int] = 0


class BigSetCreate(CamelModel):
    description: str
    created: datetime
    number_of_sets: int

class AddSetToBigSetRequest(CamelModel):
    description: str


class BigSetResponse(CamelModel):
    id: int
    description: str
    created: datetime
    finished: Optional[datetime]


class SetResponse(SetBase):
    id: int


class BigSetFull(CamelModel):
    id: int
    description: str
    created: datetime
    finished: Optional[datetime]
    sets: list[SetResponse]

