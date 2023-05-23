from __future__ import annotations

from bson import ObjectId
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')


class MyConfig:
    allow_population_by_field_name = True
    anystr_strip_whitespace = True
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}


class Paging(BaseModel):
    total: int
    limit: int
    offset: int


class ListModel(GenericModel, Generic[T]):
    results: List[T]
    paging: Paging

    class Config(MyConfig):
        ...


class SuccessfulResponse(BaseModel):
    detail: str


class AuthenticateResponse(BaseModel):
    access_token: str
