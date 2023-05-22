from fastapi import HTTPException, status


class ThinkificCreateError(HTTPException):
    def __init__(self, thinkific_collection: str, thinkific_error: str):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Error when creating item at {thinkific_collection} collection in thinkific. ERROR: {thinkific_error}",
                         None)


class ThinkificUpdateError(HTTPException):
    def __init__(self, thinkific_collection: str, thinkific_error: str):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Error when updating item at {thinkific_collection} collection in thinkific. ERROR: {thinkific_error}",
                         None)


class ThinkificDeleteError(HTTPException):
    def __init__(self, thinkific_collection: str, thinkific_error: str):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Error when deleting item from {thinkific_collection} collection in thinkific. ERROR: {thinkific_error}",
                         None)
