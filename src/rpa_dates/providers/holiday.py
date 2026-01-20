import holidays as py_holidays_lib
from datetime import date
from rpa_dates.interfaces import HolidayProvider
from rpa_dates.exceptions import HolidayApiError


class LocalPythonHolidayProvider(HolidayProvider):
    """
    Uses the local 'holidays' Python library.
    """

    def get_holidays(self, year: int, country_code: str) -> set[date]:
        try:
            country_holidays = py_holidays_lib.country_holidays(country_code, years=year)
            return set(country_holidays.keys())

        except NotImplementedError:
            # Raised if the library doesn't support the country code
            raise HolidayApiError(f"Country code '{country_code}' not supported by local library.")
        except Exception as e:
            raise HolidayApiError(f"Local holiday error: {e}")
