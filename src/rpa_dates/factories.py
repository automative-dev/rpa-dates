from .providers.holiday import LocalPythonHolidayProvider
from .providers.nager_date_v3 import NagerDateV3Provider
from .providers.nager_date_v4 import NagerDateV4Provider
from .providers import OpenHolidaysProvider
from .providers.fallback import FallbackHolidayProvider

from .interfaces import HolidayProvider


class ProviderFactory:
    @staticmethod
    def create_provider(timeout: int = 10) -> HolidayProvider:
        """
        Creates a provider chain:
        1. holidays Python library (Primary)
        2. Nager.Date v3 (Backup)
        3. Nager.Date v4 (Backup)
        4. OpenHolidays (Backup)
        """
        holidays = LocalPythonHolidayProvider()
        nager_date_v3 = NagerDateV3Provider(timeout=timeout)
        nager_date_v4 = NagerDateV4Provider(timeout=timeout)
        open_holidays = OpenHolidaysProvider(timeout=timeout)

        return FallbackHolidayProvider([holidays, nager_date_v3, nager_date_v4, open_holidays])
