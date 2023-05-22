from fastapi import HTTPException, status
from typing import Union
from bson import ObjectId


class ResourceNotFound(HTTPException):
    def __init__(self, resource_id: Union[str, ObjectId], resource_name: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"{resource_name} {resource_id} not found", None)


class ResourceNotAvailable(HTTPException):
    def __init__(self, resource_id: Union[str, ObjectId], resource_name: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"{resource_name} {resource_id} not available", None)


class DuplicatedKey(HTTPException):
    def __init__(self, key):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"Duplicated key {key}", None)


class ResourceReference(HTTPException):
    def __init__(self, resource_to_delete, resource_reference):
        super().__init__(status.HTTP_400_BAD_REQUEST,
                         f"Unable to delete {resource_to_delete}. {resource_to_delete} is currently being referenced by a {resource_reference}(s).",
                         None)
