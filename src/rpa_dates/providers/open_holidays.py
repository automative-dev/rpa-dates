import functools
import requests
from datetime import datetime, date

from rpa_dates.interfaces import HolidayProvider
from rpa_dates.exceptions import HolidayApiError


class OpenHolidaysProvider(HolidayProvider):
    """
    This provider fetches public holidays from the OpenHolidays API.
    It maps the 'year' request to a full-year date range (Jan 1 - Dec 31).
    """
    _API_URL = 'https://openholidaysapi.org/PublicHolidays'

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @functools.lru_cache(maxsize=64)
    def get_holidays(self, year: int, country_code: str) -> set[date]:
        params = {
            "countryIsoCode": country_code,
            "languageIsoCode": "EN",
            "validFrom": f"{year}-01-01",
            "validTo": f"{year}-12-31"
        }

        try:
            response = requests.get(self._API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            return {
                datetime.strptime(item['startDate'], '%Y-%m-%d').date()
                for item in data
            }

        except requests.RequestException as e:
            # Catch connection errors, timeouts, or HTTP errors (4xx/5xx)
            raise HolidayApiError(f"Failed to fetch holidays for {country_code} from OpenHolidays: {e}")
        except (KeyError, ValueError) as e:
            # Catch parsing errors if the API response format changes
            raise HolidayApiError(f"Failed to parse response from OpenHolidays: {e}")
