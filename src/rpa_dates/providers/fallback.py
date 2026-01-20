import logging
from datetime import date

from rpa_dates.interfaces import HolidayProvider
from rpa_dates.exceptions import HolidayApiError

logger = logging.getLogger(__name__)


class FallbackHolidayProvider(HolidayProvider):
    """
    A composite provider that tries multiple providers in sequence.
    If the first one fails (raises HolidayApiError), it tries the next.
    """

    def __init__(self, providers: list[HolidayProvider]):
        self.providers = providers

    def get_holidays(self, year: int, country_code: str) -> set[date]:
        last_error = None

        for provider in self.providers:
            provider_name = provider.__class__.__name__
            try:
                return provider.get_holidays(year, country_code)

            except HolidayApiError as e:
                logger.warning(f"Provider '{provider_name}' failed: {e}. Switching to next provider...")
                last_error = e
                continue

        raise HolidayApiError(f"All holiday providers failed. Last error: {last_error}")
