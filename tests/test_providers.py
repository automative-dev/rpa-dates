import pytest
from unittest.mock import Mock, patch
from datetime import date
from requests.exceptions import Timeout, HTTPError

from rpa_dates.providers.fallback import FallbackHolidayProvider
from rpa_dates.providers.nager_date_v3 import NagerDateV3Provider
from rpa_dates.providers.open_holidays import OpenHolidaysProvider
from rpa_dates.providers.holiday import LocalPythonHolidayProvider
from rpa_dates.exceptions import HolidayApiError


def test_fallback_uses_primary_if_successful():
    """If primary works, secondary should never be called."""
    primary = Mock()
    primary.get_holidays.return_value = {date(2025, 1, 1)}

    backup = Mock()

    provider = FallbackHolidayProvider([primary, backup])
    result = provider.get_holidays(2025, "US")

    assert date(2025, 1, 1) in result
    primary.get_holidays.assert_called_once()
    backup.get_holidays.assert_not_called()


def test_fallback_switches_on_error():
    """If primary fails, it must call backup."""
    primary = Mock()
    # Simulate Primary crashing
    primary.get_holidays.side_effect = HolidayApiError("Primary down")

    backup = Mock()
    backup.get_holidays.return_value = {date(2025, 12, 25)}

    provider = FallbackHolidayProvider([primary, backup])
    result = provider.get_holidays(2025, "US")

    assert date(2025, 12, 25) in result
    primary.get_holidays.assert_called_once()
    backup.get_holidays.assert_called_once()


def test_fallback_raises_if_all_fail():
    """If all providers fail, the fallback itself must raise an error."""
    p1 = Mock()
    p1.get_holidays.side_effect = HolidayApiError("Fail 1")
    p2 = Mock()
    p2.get_holidays.side_effect = HolidayApiError("Fail 2")

    provider = FallbackHolidayProvider([p1, p2])

    with pytest.raises(HolidayApiError, match="All holiday providers failed"):
        provider.get_holidays(2025, "US")


# --- 2. Nager.Date API Tests (Mocking Requests) ---


@patch("requests.get")
def test_nager_v3_success(mock_get):
    """Test parsing of Nager V3 JSON response."""
    # Mock the API response structure
    mock_get.return_value.json.return_value = [{"date": "2025-01-01", "name": "New Year"}, {"date": "2025-12-25", "name": "Christmas"}]
    mock_get.return_value.raise_for_status = Mock()

    provider = NagerDateV3Provider()
    result = provider.get_holidays(2025, "US")

    assert date(2025, 1, 1) in result
    assert len(result) == 2


@patch("requests.get")
def test_nager_v3_http_error(mock_get):
    """Test that HTTP errors are converted to HolidayApiError."""
    mock_get.side_effect = Timeout("Connection timed out")

    provider = NagerDateV3Provider()

    with pytest.raises(HolidayApiError, match="Failed to fetch holidays"):
        provider.get_holidays(2025, "XX")


# --- 3. OpenHolidays API Tests ---


@patch("requests.get")
def test_open_holidays_success(mock_get):
    """Test parsing of OpenHolidays JSON response."""
    # OpenHolidays uses 'startDate' key
    mock_get.return_value.json.return_value = [{"startDate": "2025-07-04", "id": "123"}]

    provider = OpenHolidaysProvider()
    result = provider.get_holidays(2025, "US")

    assert date(2025, 7, 4) in result
    # Verify we constructed the URL query params correctly
    args, kwargs = mock_get.call_args
    assert kwargs["params"]["validFrom"] == "2025-01-01"
    assert kwargs["params"]["validTo"] == "2025-12-31"


# --- 4. Local Provider Tests ---


def test_local_provider_success():
    """Test valid country code (requires 'holidays' lib installed)."""
    provider = LocalPythonHolidayProvider()
    result = provider.get_holidays(2025, "US")

    # We expect standard US holidays to be present
    assert date(2025, 7, 4) in result  # Independence Day
    assert date(2025, 12, 25) in result  # Christmas


def test_local_provider_invalid_country():
    """Test invalid country code raises correct error."""
    provider = LocalPythonHolidayProvider()

    # 'ZZ' is not a valid ISO country code in the holidays library
    with pytest.raises(HolidayApiError, match="not supported"):
        provider.get_holidays(2025, "ZZ")
