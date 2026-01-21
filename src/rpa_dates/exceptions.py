class DateOperationError(Exception):
    """Base exception for date related errors."""

    pass


class HolidayApiError(DateOperationError):
    """Raised when external holiday provider fails."""

    pass
