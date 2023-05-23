from pydantic import BaseModel
from bson import ObjectId
from typing import Any


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class EnvisionBaseModel(BaseModel):
    def __init__(self, **data: Any):
        if '_id' in data and 'id' not in data:
            data.update(id=data.pop('_id'))
        super().__init__(**data)

    def dict(self, *args, **kwargs):
        kwargs['by_alias'] = True
        return super().dict(*args, **kwargs)

    class Config:
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
