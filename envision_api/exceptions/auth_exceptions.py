from fastapi import HTTPException, status


class AdminNotAllowed(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, 'The admin is not allowed to perform the requested action', None)


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, 'Invalid token', None)


class ExpiredToken(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, 'Token expired', None)
