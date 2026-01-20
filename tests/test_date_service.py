import pytest
from datetime import date, datetime
from rpa_dates.exceptions import DateOperationError

# --- Normalization Tests ---

@pytest.mark.parametrize("input_date, expected_str", [
    ("2025-01-01", "2025-01-01"),
    (date(2025, 1, 1), "2025-01-01"),
    (datetime(2025, 1, 1, 12, 0, 0), "2025-01-01"),
])
def test_normalize_valid_inputs(service, input_date, expected_str):
    """Test normalization of string, date, and datetime inputs."""
    result = service.normalize(input_date, input_format="%Y-%m-%d")
    assert isinstance(result, datetime)
    assert result.strftime("%Y-%m-%d") == expected_str


def test_normalize_none(service):
    """Test that None returns the current datetime."""
    # We allow a small delta for 'now' execution time
    now = datetime.now()
    result = service.normalize(None)
    assert abs((result - now).total_seconds()) < 1


def test_normalize_invalid_string(service):
    """Test that invalid string formats raise DateOperationError."""
    with pytest.raises(DateOperationError):
        service.normalize("2025/01/01", input_format="%Y-%m-%d")


# --- Basic Date Logic Tests ---

def test_first_last_day_of_month(service):
    dt = date(2025, 2, 15)  # Feb 2025
    assert service.first_day_of_month(dt).day == 1
    assert service.last_day_of_month(dt).day == 28  # Non-leap year


def test_week_of_year_iso(service):
    # Jan 1st, 2025 is a Wednesday. ISO week 1.
    assert service.week_of_year("2025-01-01", standard="iso") == 1


def test_fiscal_year(service):
    # Fiscal year starts in April (month 4)
    assert service.fiscal_year("2025-03-31", start_month=4) == 2024
    assert service.fiscal_year("2025-04-01", start_month=4) == 2025


# --- Working Day Logic Tests (The Core Logic) ---

def test_get_working_days_in_month_excludes_weekends(service, mock_provider):
    """Verify weekends are automatically excluded."""
    # Jan 2025: 1st is Wed. 4th (Sat) and 5th (Sun) are weekends.
    mock_provider.get_holidays.return_value = set()  # No holidays

    days = service.get_working_days_in_month("01.01.2025")

    # Check that Jan 4th and Jan 5th are NOT in the list
    dates = [d.date() for d in days]
    assert date(2025, 1, 4) not in dates
    assert date(2025, 1, 5) not in dates
    assert date(2025, 1, 6) in dates  # Monday


def test_get_working_days_excludes_holidays(service, mock_provider):
    """Verify holidays are excluded."""
    # Let's say Jan 6th (Mon) is a holiday
    mock_provider.get_holidays.return_value = {date(2025, 1, 6)}

    days = service.get_working_days_in_month("2025-01-01", country_code="US")
    dates = [d.date() for d in days]

    assert date(2025, 1, 6) not in dates  # Should be excluded
    assert date(2025, 1, 7) in dates  # Tuesday


def test_nth_working_day_success(service, mock_provider):
    """Test finding the Nth working day."""
    # Jan 2025 starts on Wednesday.
    # 1st: Wed (Work)
    # 2nd: Thu (Work)
    # 3rd: Fri (Work)
    # 4th: Sat (Skip)
    # 5th: Sun (Skip)
    # 6th: Mon (Holiday - let's mock it)
    # 7th: Tue (Work)

    mock_provider.get_holidays.return_value = {date(2025, 1, 6)}  # Jan 6 holiday

    # We want the 4th working day.
    # Working days: 1st, 2nd, 3rd, (skip 4,5,6), 7th.
    # So 4th working day is Jan 7th.
    result = service.nth_working_day_of_month(4, "2025-01-01", country_code="US")
    assert result.date() == date(2025, 1, 7)


def test_nth_working_day_out_of_bounds(service):
    """Test error when n is larger than working days in month."""
    with pytest.raises(ValueError, match="Month has fewer than"):
        service.nth_working_day_of_month(30, "2025-02-01")  # Feb has max 28 days


# --- Complex Offset Logic (Year Boundary) ---

def test_working_day_offset_simple(service, mock_provider):
    """Test simple offset within the same week."""
    # Friday Jan 3rd 2025 -> Add 1 working day -> Monday Jan 6th
    mock_provider.get_holidays.return_value = set()

    start = date(2025, 1, 3)
    result = service.working_day_offset(1, start, country_code="US")
    assert result.date() == date(2025, 1, 6)


def test_working_day_offset_year_boundary(service, mock_provider):
    """
    CRITICAL: Test offset crossing from Dec to Jan with holidays in both years.
    Start: Dec 30, 2024 (Monday)
    Add 3 working days.
    - Dec 31 (Tue) -> Work
    - Jan 1 (Wed) -> Holiday (New Year)
    - Jan 2 (Thu) -> Work
    - Jan 3 (Fri) -> Work (Target)
    """

    # Define behavior for get_holidays based on input year
    def side_effect(year, country_code):
        if year == 2024:
            return set()
        if year == 2025:
            return {date(2025, 1, 1)}
        return set()

    mock_provider.get_holidays.side_effect = side_effect

    start = date(2024, 12, 30)
    # 1: Dec 31, Skip Jan 1, 2: Jan 2, 3: Jan 3
    result = service.working_day_offset(3, start, country_code="US")

    assert result.date() == date(2025, 1, 3)

    # Verify provider was called for both years
    # Note: args are passed as (year, code)
    calls = mock_provider.get_holidays.call_args_list
    years_called = [call.args[0] for call in calls]
    assert 2024 in years_called
    assert 2025 in years_called


def test_working_day_offset_negative(service, mock_provider):
    """Test going backwards."""
    # Jan 6th 2025 (Mon) - 1 working day -> Jan 3rd 2025 (Fri)
    mock_provider.get_holidays.return_value = set()

    start = date(2025, 1, 6)
    result = service.working_day_offset(-1, start, country_code="US")
    assert result.date() == date(2025, 1, 3)


def test_working_day_offset_zero(service):
    """Test 0 offset returns same date."""
    start = date(2025, 1, 1)
    result = service.working_day_offset(0, start)
    assert result.date() == start


# --- Caching & Types Tests ---

def test_public_holidays_caching_call_structure(service, mock_provider):
    """
    Ensure the service converts list inputs to tuples internally
    so lru_cache doesn't crash.
    """
    mock_provider.get_holidays.return_value = {date(2025, 1, 1)}

    # Passing a LIST to public_holidays
    holidays = service.public_holidays([2025], country_code="US")

    assert date(2025, 1, 1) in holidays
    # Ensure no crash