from fastapi import HTTPException, status


class UserWithoutPassword(HTTPException):
    def __init__(self, user_id):
        super().__init__(status.HTTP_404_NOT_FOUND, f"User {user_id} has no password", None)


class WrongPassword(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Wrong password", None)


class MissingPassword(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, f"User has login with password but not password was provided", None)
