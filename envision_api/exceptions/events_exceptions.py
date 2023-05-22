from fastapi import HTTPException, status


class EventsOverlap(HTTPException):
    def __init__(self, events: list):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Event has overlap with the following events: {events}", None)


class EventDatesInverted(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"End date should be greater than the start date", None)


class EventTooShortDuration(HTTPException):
    def __init__(self, minimum_duration: int):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Event duration should be greater than {minimum_duration} minutes", None)

class EventTooLongDuration(HTTPException):
    def __init__(self, maximum_duration: int):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Event duration should be lower than {maximum_duration} hours", None)


class MissingDate(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, f"start_date and end_date should be both null or both datetime",
                         None)
