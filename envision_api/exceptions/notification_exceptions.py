from fastapi import HTTPException, status


class SendAtPast(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"send_at can not be a date in the past, to send a notification now send_at should not be present",
                         None)


class CancelNotificationException(HTTPException):
    def __init__(self, notification_status):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Notifications with status {notification_status} can not be canceled", None)


class UpdateNotificationException(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Updates are only possible for scheduled notifications", None)
