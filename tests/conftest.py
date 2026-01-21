import pytest
from unittest.mock import Mock
from rpa_dates.service import DateService
from rpa_dates.interfaces import HolidayProvider
from rpa_dates.config import  DateConfig


# --- Fixtures ---
@pytest.fixture
def date_config():
    return DateConfig(
        api_timeout_seconds=5,
        default_input_format='%Y-%m-%d',
        default_output_format='%d.%m.%Y',
        fiscal_year_start_month=4,
    )

@pytest.fixture
def mock_provider():
    """Creates a mock holiday provider."""
    provider = Mock(spec=HolidayProvider)
    # Default: No holidays unless specified
    provider.get_holidays.return_value = set()
    return provider


@pytest.fixture
def service(mock_provider, date_config):
    """Creates a DateService instance with the mock provider."""
    return DateService(holiday_provider=mock_provider, config=date_config)
