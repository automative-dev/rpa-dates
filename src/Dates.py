""" Delivers methods to operate with dates and times objects. """

from typing import Literal, Optional
import calendar
import requests
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, datetime
import functools

DateInput = Optional[str | date | datetime]


class Dates:
    """ Delivers stateless methods to operate with dates and times objects. """

    WEEK_DAYS: dict[str, int] = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
    _PUBLIC_HOLIDAYS_API_URL = 'https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}'

    @staticmethod
    def _to_datetime(date_input: DateInput, date_format: str = '%d.%m.%Y') -> datetime:
        """Internal helper to reliably convert various inputs to a datetime object."""
        if date_input is None:
            return datetime.today()
        if isinstance(date_input, datetime):
            return date_input
        if isinstance(date_input, date):
            return datetime.combine(date_input, datetime.min.time())
        if isinstance(date_input, str):
            return datetime.strptime(date_input, date_format)
        raise TypeError(f"Unsupported type for date_input: {type(date_input)}")

    @staticmethod
    def new_datetime(
            day: int,
            month: int,
            year: int,
            hour: int = 0,
            minute: int = 0,
            second: int = 0,
            output_format: str = '%d.%m.%Y',
            format: Literal['str', 'datetime'] = 'str'
    ) -> str | datetime:
        """Return new date in given format (default: %d.%m.%Y) or datetime object."""
        dt = datetime(year, month, day, hour, minute, second)
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def convert_to_datetime(date_string: str, date_format: str = '%d.%m.%Y') -> datetime:
        """Convert string date to datetime object using given date format."""
        return datetime.strptime(date_string, date_format)

    @staticmethod
    def change_date_format(date_string: str, date_format: str = '%d.%m.%Y', output_format: str = '%d.%m.%Y') -> str:
        """Convert the date from one format to another."""
        dt = datetime.strptime(date_string, date_format)
        return dt.strftime(output_format)

    @staticmethod
    def offset(
            date_input: DateInput,
            date_format: str = '%d.%m.%Y',
            days: int = 0,
            months: int = 0,
            years: int = 0,
            output_format: str = '%d.%m.%Y',
            format: Literal['str', 'datetime'] = 'str'
    ) -> str | datetime:
        """Returns new date by applying an offset of days, months, or years."""
        dt = Dates._to_datetime(date_input, date_format)
        # Use a single relativedelta for cleaner code
        dt += relativedelta(years=years, months=months, days=days)
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def today(output_format='%d.%m.%Y', format: Literal['str', 'datetime'] = 'str') -> str | datetime:
        """Returns today's date."""
        dt = datetime.today()
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def yesterday(output_format='%d.%m.%Y', format: Literal['str', 'datetime'] = 'str') -> str | datetime:
        """Returns yesterday's date."""
        dt = datetime.today() - timedelta(days=1)
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def tomorrow(output_format='%d.%m.%Y', format: Literal['str', 'datetime'] = 'str') -> str | datetime:
        """Returns tomorrow's date."""
        dt = datetime.today() + timedelta(days=1)
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def next_working_day(
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            country_code: Optional[str] = None,
            output_format: str = '%d.%m.%Y',
            format: Literal["str", "datetime"] = 'str'
    ) -> str | datetime:
        """Returns the next working day, skipping weekends and optionally public holidays."""
        dt = Dates._to_datetime(date_input, date_format)

        holidays = set()
        if country_code:
            # Fetches for current and next year in case the date is at year-end
            holidays.update(Dates.get_public_holidays(country_code, dt.year, dates_only=True, date_format=date_format))
            holidays.update(Dates.get_public_holidays(country_code, dt.year + 1, dates_only=True, date_format=date_format))

        next_day = dt + timedelta(days=1)
        while next_day.weekday() >= 5 or (country_code and next_day.strftime(date_format) in holidays):
            next_day += timedelta(days=1)

        return next_day.strftime(output_format) if format == 'str' else next_day

    @staticmethod
    def previous_working_day(
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            country_code: Optional[str] = None,
            output_format: str = '%d.%m.%Y',
            format: Literal["str", "datetime"] = 'str'
    ) -> str | datetime:
        """Returns the previous working day, skipping weekends and optionally public holidays."""
        dt = Dates._to_datetime(date_input, date_format)

        holidays = set()
        if country_code:
            # Fetches for current and previous year in case the date is at year-start
            holidays.update(Dates.get_public_holidays(country_code, dt.year, dates_only=True, date_format=date_format))
            holidays.update(Dates.get_public_holidays(country_code, dt.year - 1, dates_only=True, date_format=date_format))

        prev_day = dt - timedelta(days=1)
        while prev_day.weekday() >= 5 or (country_code and prev_day.strftime(date_format) in holidays):
            prev_day -= timedelta(days=1)

        return prev_day.strftime(output_format) if format == 'str' else prev_day

    @staticmethod
    def first_day_of_month(
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            output_format="%d.%m.%Y",
            format: Literal["str", "datetime"] = 'str'
    ) -> str | datetime:
        """Returns the first day of the month for the given date."""
        dt = Dates._to_datetime(date_input, date_format).replace(day=1)
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def last_day_of_month(
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            output_format="%d.%m.%Y",
            format: Literal["str", "datetime"] = 'str'
    ) -> str | datetime:
        """Returns the last day of the month for the given date."""
        dt = Dates._to_datetime(date_input, date_format)
        _, last_day = calendar.monthrange(dt.year, dt.month)
        dt = dt.replace(day=last_day)
        return dt.strftime(output_format) if format == 'str' else dt

    @staticmethod
    def calculate_date_of_weekday(
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            week_day: Literal['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] = 'mon',
            output_format="%d.%m.%Y",
            format: Literal["str", "datetime"] = 'str'
    ) -> str | datetime:
        """Calculates the date of a specific weekday within the week of the given date."""
        dt = Dates._to_datetime(date_input, date_format)
        start_of_week = dt - timedelta(days=dt.weekday())
        target_date = start_of_week + timedelta(days=Dates.WEEK_DAYS[week_day])
        return target_date.strftime(output_format) if format == 'str' else target_date

    @staticmethod
    def day_of_year(date_input: DateInput = None, date_format: str = '%d.%m.%Y') -> int:
        """Returns the day of the year (1-366)."""
        dt = Dates._to_datetime(date_input, date_format)
        return dt.timetuple().tm_yday

    @staticmethod
    def week_of_year(date_input: DateInput = None, date_format: str = '%d.%m.%Y', iso_format: bool = True) -> int:
        """Returns the week number of the year."""
        dt = Dates._to_datetime(date_input, date_format)
        if iso_format:
            return dt.isocalendar().week
        else:
            # %U - Sunday as first day, %W - Monday as first day
            return int(dt.strftime('%W'))

    @staticmethod
    def difference_between_dates(
            first_date: DateInput,
            second_date: DateInput,
            date_format: str = '%d.%m.%Y',
            unit: Literal['seconds', 'minutes', 'hours', 'days'] = 'days'
    ) -> int:
        """Calculates the absolute difference between two dates in the specified unit."""
        dt1 = Dates._to_datetime(first_date, date_format)
        dt2 = Dates._to_datetime(second_date, date_format)
        diff = abs(dt1 - dt2)

        if unit == 'days':
            return diff.days

        total_seconds = diff.total_seconds()
        if unit == 'seconds':
            return int(total_seconds)
        if unit == 'minutes':
            return int(total_seconds / 60)
        if unit == 'hours':
            return int(total_seconds / 3600)
        return diff.days

    @staticmethod
    def get_fiscal_year(date_input: DateInput = None, date_format: str = '%d.%m.%Y', start_month: int = 4) -> int:
        """Return the fiscal year for given date."""
        dt = Dates._to_datetime(date_input, date_format)
        return dt.year if dt.month < start_month else dt.year + 1

    @staticmethod
    def get_fiscal_month(date_input: DateInput = None, date_format: str = '%d.%m.%Y', start_month: int = 4) -> int:
        """Return the fiscal month for given date."""
        dt = Dates._to_datetime(date_input, date_format)
        return (dt.month - start_month + 12) % 12 + 1

    @staticmethod
    @functools.lru_cache(maxsize=32)
    def get_public_holidays(country_code: str, year: int, dates_only: bool = True, date_format: str = '%d.%m.%Y') -> list[str] | dict:
        """
        Return holidays for given year and country. Results are cached.
        List of countries: https://date.nager.at/Country
        """
        url = Dates._PUBLIC_HOLIDAYS_API_URL.format(year=year, country_code=country_code)
        response = requests.get(url)
        response.raise_for_status()

        holidays_raw = response.json()

        if dates_only:
            return [Dates.change_date_format(item['date'], '%Y-%m-%d', date_format) for item in holidays_raw]
        else:
            return {Dates.change_date_format(item['date'], '%Y-%m-%d', date_format): item['name'] for item in holidays_raw}

    @staticmethod
    def is_public_holiday(country_code: str, date_input: DateInput = None, date_format: str = '%d.%m.%Y') -> bool:
        """Check if a given date is a public holiday in the specified country."""
        dt = Dates._to_datetime(date_input, date_format)
        holidays = Dates.get_public_holidays(country_code, dt.year, dates_only=True, date_format=date_format)
        return dt.strftime(date_format) in holidays

    @staticmethod
    def nth_working_day_of_month(
            n: int,
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            holidays: Optional[list[str]] = None,
            output_format: str = "%d.%m.%Y",
            format: Literal['str', 'datetime'] = 'str'
    ) -> str | datetime:
        """Returns the nth working day of the month."""
        if n <= 0:
            raise ValueError("Day 'n' must be a positive integer.")

        dt = Dates._to_datetime(date_input, date_format)
        current_day = dt.replace(day=1)

        holiday_set = set(holidays) if holidays else set()

        working_days_found = 0
        while working_days_found < n:
            # Check if current_day is within the same month
            if current_day.month != dt.month:
                raise ValueError(f"Month has fewer than {n} working days.")

            if current_day.weekday() < 5 and current_day.strftime(date_format) not in holiday_set:
                working_days_found += 1

            if working_days_found < n:
                current_day += timedelta(days=1)

        return current_day.strftime(output_format) if format == 'str' else current_day

    @staticmethod
    def working_day_offset(
            days_offset: int,
            date_input: DateInput = None,
            date_format: str = '%d.%m.%Y',
            holidays: Optional[list[str]] = None,
            output_format: str = "%d.%m.%Y",
            format: Literal['str', 'datetime'] = 'str'
    ) -> str | datetime:
        """Calculates a date by offsetting a number of working days."""
        if days_offset == 0:
            return Dates._to_datetime(date_input, date_format)

        dt = Dates._to_datetime(date_input, date_format)
        holiday_set = set(holidays) if holidays else set()
        step = timedelta(days=1) if days_offset > 0 else timedelta(days=-1)

        days_counted = 0
        current_date = dt
        while days_counted < abs(days_offset):
            current_date += step
            if current_date.weekday() < 5 and current_date.strftime(date_format) not in holiday_set:
                days_counted += 1

        return current_date.strftime(output_format) if format == 'str' else current_date
