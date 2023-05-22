from fastapi import HTTPException, status


class InvalidMail(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, 'Invalid mail', None)


class RejectedMail(HTTPException):
    def __init__(self, reason):
        super().__init__(status.HTTP_404_NOT_FOUND, f'Mail rejected. Reject reason: {reason}', None)


class ErrorMail(HTTPException):
    def __init__(self, detail):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f'An error occurred when sending the mail. Error detail: {detail}',
                         None)
