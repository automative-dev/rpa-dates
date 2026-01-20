import pytest
from unittest.mock import Mock
from rpa_dates.service import DateService
from rpa_dates.interfaces import HolidayProvider


# --- Fixtures ---

@pytest.fixture
def mock_provider():
    """Creates a mock holiday provider."""
    provider = Mock(spec=HolidayProvider)
    # Default: No holidays unless specified
    provider.get_holidays.return_value = set()
    return provider


@pytest.fixture
def service(mock_provider):
    """Creates a DateService instance with the mock provider."""
    return DateService(holiday_provider=mock_provider)
