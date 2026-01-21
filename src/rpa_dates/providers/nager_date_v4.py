import functools
import requests
from datetime import datetime, date

from rpa_dates.interfaces import HolidayProvider
from rpa_dates.exceptions import HolidayApiError


class NagerDateV4Provider(HolidayProvider):
    """
    This provider fetches public holidays from the Nager.Date API v3.
    It caches results to avoid redundant API calls for the same year and country code.
    """

    _API_URL = "https://date.nager.at/api/v4/PublicHolidays/{year}/{country_code}"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @functools.lru_cache(maxsize=64)
    def get_holidays(self, year: int, country_code: str) -> set[date]:
        url = self._API_URL.format(year=year, country_code=country_code)
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return {datetime.strptime(item["date"], "%Y-%m-%d").date() for item in data}
        except requests.RequestException as e:
            raise HolidayApiError(f"Failed to fetch holidays for {country_code}: {e}")
