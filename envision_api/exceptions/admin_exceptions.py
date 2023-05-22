from fastapi import HTTPException, status


class InvalidSpice(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, 'Invalid Spice', None)


class MissingTalentId(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, 'Role talent should have talent_id field', None)
