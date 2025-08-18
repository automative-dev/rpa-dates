import pytest
from datetime import datetime, date
from unittest.mock import Mock
from src.Dates import Dates

# Mock data for Nager API for Poland, 2025
MOCK_HOLIDAYS_PL_2025 = [
    {"date": "2025-01-01", "localName": "Nowy Rok", "name": "New Year's Day"},
    {"date": "2025-01-06", "localName": "Święto Trzech Króli", "name": "Epiphany"},
    {"date": "2025-04-20", "localName": "Niedziela Wielkanocna", "name": "Easter Sunday"},
    {"date": "2025-04-21", "localName": "Poniedziałek Wielkanocny", "name": "Easter Monday"},
    {"date": "2025-05-01", "localName": "Święto Pracy", "name": "Labour Day"},
    {"date": "2025-05-03", "localName": "Święto Narodowe Trzeciego Maja", "name": "Constitution Day"},
    {"date": "2025-06-08", "localName": "Zielone Świątki", "name": "Pentecost Sunday"},
    {"date": "2025-06-19", "localName": "Boże Ciało", "name": "Corpus Christi"},
    {"date": "2025-08-15", "localName": "Wniebowzięcie Najświętszej Maryi Panny", "name": "Assumption Day"},
    {"date": "2025-11-01", "localName": "Wszystkich Świętych", "name": "All Saints' Day"},
    {"date": "2025-11-11", "localName": "Narodowe Święto Niepodległości", "name": "Independence Day"},
    {"date": "2025-12-25", "localName": "pierwszy dzień Bożego Narodzenia", "name": "Christmas Day"},
    {"date": "2025-12-26", "localName": "drugi dzień Bożego Narodzenia", "name": "St. Stephen's Day"}
]

@pytest.fixture
def mock_requests_get(mocker):
    """Fixture to mock requests.get for holiday API calls."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = MOCK_HOLIDAYS_PL_2025
    
    # Patch requests.get to return our mock response
    return mocker.patch('requests.get', return_value=mock_response)

# --- Test Core & Helper Methods ---

def test_to_datetime_conversion():
    """Tests the internal _to_datetime helper."""
    dt_obj = datetime(2025, 8, 18)
    date_obj = date(2025, 8, 18)
    str_obj = "18.08.2025"
    
    assert Dates._to_datetime(dt_obj) == dt_obj
    assert Dates._to_datetime(date_obj) == dt_obj
    assert Dates._to_datetime(str_obj) == dt_obj
    with pytest.raises(TypeError):
        Dates._to_datetime(12345)

# --- Test Date Creation and Formatting ---

def test_new_datetime():
    assert Dates.new_datetime(18, 8, 2025) == "18.08.2025"
    assert Dates.new_datetime(18, 8, 2025, format='datetime') == datetime(2025, 8, 18)
    assert Dates.new_datetime(1, 1, 2024, output_format='%Y/%m/%d') == "2024/01/01"


def test_change_date_format():
    assert Dates.change_date_format("2025-08-18", "%Y-%m-%d", "%d/%m/%Y") == "18/08/2025"


# --- Test Relative Dates & Offsets ---
def test_offset():
    base_date = "15.02.2024"  # A leap year
    assert Dates.offset(base_date, days=15) == "01.03.2024"
    assert Dates.offset(base_date, days=-15) == "31.01.2024"
    assert Dates.offset("31.01.2025", months=1) == "28.02.2025"
    assert Dates.offset("29.02.2024", years=1, format='datetime') == datetime(2025, 2, 28, 0, 0)


def test_today_yesterday_tomorrow(mocker):
    """Mocks datetime.today to create a deterministic test."""
    mock_today = datetime(2025, 8, 18, 12, 0, 0)
    mocker.patch('src.Dates.datetime').today.return_value = mock_today

    assert Dates.today() == "18.08.2025"
    assert Dates.yesterday() == "17.08.2025"
    assert Dates.tomorrow(format='datetime') == datetime(2025, 8, 19, 12, 0, 0)

# --- Test Boundary and Property Calculations ---

def test_first_and_last_day_of_month():
    assert Dates.first_day_of_month("18.08.2025") == "01.08.2025"
    assert Dates.last_day_of_month("18.08.2025") == "31.08.2025"
    # Leap year check
    assert Dates.last_day_of_month("10.02.2024", format='datetime') == datetime(2024, 2, 29)
    # Non-leap year
    assert Dates.last_day_of_month("10.02.2025", format='datetime') == datetime(2025, 2, 28)

@pytest.mark.parametrize("date_in, unit, expected", [
    (("18.08.2025", "28.08.2025"), "days", 10),
    (("18.08.2025 10:00", "18.08.2025 12:00"), "hours", 2),
    (("18.08.2025 10:00", "18.08.2025 10:05"), "minutes", 5),
    (("18.08.2025 10:00:15", "18.08.2025 10:00:45"), "seconds", 30)
])
def test_difference_between_dates(date_in, unit, expected):
    date1, date2 = date_in
    date_format = '%d.%m.%Y'
    if ' ' in date1:
        date_format = '%d.%m.%Y %H:%M' if ':' in date1.split(' ')[1] else '%d.%m.%Y %H'
        if date1.count(':') == 2:
            date_format = '%d.%m.%Y %H:%M:%S'

    result = Dates.difference_between_dates(date1, date2, date_format=date_format, unit=unit)
    assert result == expected


def test_day_and_week_of_year():
    assert Dates.day_of_year("01.01.2025") == 1
    assert Dates.day_of_year("31.12.2024") == 366 # Leap year
    assert Dates.week_of_year("01.01.2025") == 1 # Wednesday, week 1
    assert Dates.week_of_year("18.08.2025") == 34 # Monday, week 34


# --- Test Holiday and Working Day Logic (with Mocks) ---
def test_get_public_holidays(mock_requests_get):
    holidays_dates = Dates.get_public_holidays("PL", 2025)
    assert "01.01.2025" in holidays_dates
    assert "15.08.2025" in holidays_dates
    assert isinstance(holidays_dates, list)

    holidays_full = Dates.get_public_holidays("PL", 2025, dates_only=False)
    assert holidays_full["11.11.2025"] == "Independence Day"
    assert isinstance(holidays_full, dict)

    # Test caching
    mock_requests_get.reset_mock()
    Dates.get_public_holidays.cache_clear()
    Dates.get_public_holidays("PL", 2025)
    Dates.get_public_holidays("PL", 2025)
    mock_requests_get.assert_called_once()


def test_is_public_holiday(mock_requests_get):
    assert Dates.is_public_holiday("PL", "15.08.2025") is True
    assert Dates.is_public_holiday("PL", "18.08.2025") is False


def test_next_working_day(mock_requests_get):
    # Standard cases (no holidays)
    assert Dates.next_working_day("13.08.2025") == "14.08.2025"  # Wed -> Thu
    assert Dates.next_working_day(date_input="15.08.2025", country_code="PL") == "18.08.2025"  # Fri(Holiday) -> Mon
    assert Dates.next_working_day("16.08.2025") == "18.08.2025"  # Sat -> Mon


def test_previous_working_day(mock_requests_get):
    assert Dates.previous_working_day("14.08.2025", country_code="PL") == "13.08.2025"  # Thu -> Wed
    assert Dates.previous_working_day("18.08.2025", country_code="PL") == "14.08.2025"  # Mon -> Prev Thu because Fri is holiday
    assert Dates.previous_working_day("17.08.2025", country_code='PL') == "14.08.2025"  # Sun -> Prev Thu


def test_nth_working_day_of_month(mock_requests_get):
    # August 2025: 15th is a holiday (Friday)
    holidays = Dates.get_public_holidays("PL", 2025)

    assert Dates.nth_working_day_of_month(1, "01.08.2025") == "01.08.2025"
    assert Dates.nth_working_day_of_month(10, "01.08.2025") == "14.08.2025"

    # With holidays provided
    assert Dates.nth_working_day_of_month(10, "01.08.2025", holidays=holidays) == "14.08.2025"
    assert Dates.nth_working_day_of_month(11, "01.08.2025", holidays=holidays) == "18.08.2025" # Skips Fri 15th

    with pytest.raises(ValueError):
        Dates.nth_working_day_of_month(0, "01.08.2025")
    with pytest.raises(ValueError):
        Dates.nth_working_day_of_month(30, "01.08.2025", holidays=holidays)  # Not enough working days


def test_working_day_offset(mock_requests_get):
    holidays = Dates.get_public_holidays("PL", 2025)  # ["15.08.2025", ...]

    # Positive offset
    assert Dates.working_day_offset(3, "12.08.2025", holidays=holidays) == "18.08.2025"  # Tue + 3 days -> Fri is holiday -> Mon

    # Negative offset
    assert Dates.working_day_offset(-3, "20.08.2025", holidays=holidays) == "14.08.2025"  # Wed - 3 days -> Fri is holiday -> Thu

    # No offset
    assert Dates.working_day_offset(0, "18.08.2025") == Dates._to_datetime("18.08.2025")
