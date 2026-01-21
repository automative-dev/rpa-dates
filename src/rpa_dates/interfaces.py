from typing import Protocol
from datetime import date


class HolidayProvider(Protocol):
    """Interface for fetching holidays."""

    def get_holidays(self, year: int, country_code: str) -> set[date]: ...
