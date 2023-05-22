from fastapi import HTTPException, status


class CMSError(HTTPException):
    def __init__(self, error_name=None):
        msg = 'CMS Error'
        if error_name:
            msg += f' {error_name}'
        super().__init__(status.HTTP_404_NOT_FOUND, msg, None)
