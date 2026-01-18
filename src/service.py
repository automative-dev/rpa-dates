import calendar
from datetime import datetime, date, timedelta
from typing import Optional, Literal
from dateutil.relativedelta import relativedelta

from .config import DateConfig
from .exceptions import DateOperationError
from .interfaces import HolidayProvider
from .providers.nager_date import NagerDateV3Provider

DateInput = str | date | datetime


class DateService:
    WEEK_DAYS = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}

    def __init__(self, config: Optional[DateConfig] = None, holiday_provider: Optional[HolidayProvider] = None):
        self.config = config or DateConfig()
        self.holiday_provider = holiday_provider or NagerDateV3Provider(self.config.api_timeout_seconds)

    def normalize(self, date_input: DateInput, input_format: Optional[str] = None) -> datetime:
        """
        Coverts DateInput (str | date | datetime) to datetime object.

        Args:
            date_input (DateInput): The date string, date, or datetime object to normalize.
            input_format (Optional[str]): The format of the input date string. If None, uses default_input_format from config.

        Returns:
            datetime: The normalized datetime object.

        Raises:
            TypeError: If date_input is of an unsupported type.
            DateOperationError: If date_input is a string and cannot be parsed with the given format.
        """
        if date_input is None:
            return datetime.now()
        if isinstance(date_input, datetime):
            return date_input
        if isinstance(date_input, date):
            return datetime.combine(date_input, datetime.min.time())
        if isinstance(date_input, str):
            format = input_format or self.config.default_input_format
            try:
                return datetime.strptime(date_input, format)
            except ValueError as e:
                raise DateOperationError(f"Could not parse '{date_input}' with format '{format}'") from e
        raise TypeError(f"Unsupported type: {type(date_input)}")

    def format(self, dt: datetime | date, output_format: Optional[str] = None) -> str:
        """
        Formats a datetime or date object into a string.

        Args:
            dt (datetime | date): The datetime or date object to format.
            output_format (Optional[str]): The desired output format. If None, uses default_output_format from config.

        Returns:
            str: The formatted date string.
        """
        fmt = output_format or self.config.default_output_format
        return dt.strftime(fmt)

    def offset(self, date_input: DateInput, seconds=0, minutes=0, hours=0, days=0, weeks=0, months=0, years=0) -> datetime:
        """
        Applies an offset of days, months, or years to a date.

        Args:
            date_input (DateInput): The date string, date, or datetime object to offset.
            seconds (int): Number of seconds to offset. Can be negative.
            minutes (int): Number of minutes to offset. Can be negative.
            hours (int): Number of hours to offset. Can be negative.
            days (int): Number of days to offset. Can be negative.
            weeks (int): Number of weeks to offset. Can be negative.
            months (int): Number of months to offset. Can be negative.
            years (int): Number of years to offset. Can be negative.

        Returns:
            datetime: The new datetime object after applying the offset.
        """
        dt = self.normalize(date_input)
        return dt + relativedelta(years=years, months=months, weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

    def first_day_of_week(self, date_input: DateInput) -> datetime:
        """
        Returns the first day of the week for the given date.

        Args:
            date_input (DateInput): The date to get the first day of the week for.

        Returns:
            datetime: The first day of the week for the given date.
        """
        dt = self.normalize(date_input)
        return dt - timedelta(days=dt.weekday())

    def last_day_of_week(self, date_input: DateInput) -> datetime:
        """
        Returns the last day of the week for the given date.

        Args:
            date_input (DateInput): The date to get the last day of the week for.

        Returns:
            datetime: The last day of the week for the given date.
        """
        dt = self.normalize(date_input)
        return dt + timedelta(days=6 - dt.weekday())

    def fist_day_of_month(self, date_input: DateInput) -> datetime:
        """
        Returns the first day of the month for the given date.

        Args:
            date_input (DateInput): The date to get the first day of the month for.

        Returns:
            datetime: The first day of the month for the given date.
        """
        dt = self.normalize(date_input)
        return dt.replace(day=1)

    def last_day_of_month(self, date_input: DateInput) -> datetime:
        """
        Returns the last day of the month for the given date.

        Args:
            date_input (DateInput): The date to get the last day of the month for.

        Returns:
            datetime: The last day of the month for the given date.
        """
        dt = self.normalize(date_input)
        _, last_day = calendar.monthrange(dt.year, dt.month)
        return dt.replace(day=last_day)

    def date_of_weekday(self, date_input: DateInput, week_day: str) -> datetime:
        """
        Calculates the date of a specific weekday within the week of the given date.

        Args:
            date_input (DateInput): The date to use as a reference.
            week_day (str): The desired weekday ('mon', 'tue', etc.).

        Returns:
            datetime: The datetime object representing the calculated weekday.
        """
        start_of_week = self.first_day_of_week(date_input)
        return start_of_week + timedelta(days=self.WEEK_DAYS[week_day])

    def day_of_year(self, date_input: DateInput) -> int:
        """
        Returns the day of the year (1-366) for the given date.

        Args:
            date_input (DateInput): The date to get the day of the year for.

        Returns:
            int: The day of the year for the given date.
        """
        dt = self.normalize(date_input)
        return dt.timetuple().tm_yday

    def week_of_year(self, date_input: DateInput, standard: Literal['iso', 'us', None] = None) -> int:
        dt = self.normalize(date_input)
        match standard:
            case 'iso':
                # ISO 8601 week number (first week of the year contains Thursday)
                return dt.isocalendar().week
            case 'us':
                # US Standard: Week 1 contains Jan 1, weeks start Sunday.
                # Logic: Calculate offset based on which day of week Jan 1 falls on.
                jan1 = dt.replace(month=1, day=1)

                # Python .weekday() is 0=Mon...6=Sun. Convert to 0=Sun...6=Sat for US logic.
                jan1_sunday_based = (jan1.weekday() + 1) % 7
                day_of_year = dt.timetuple().tm_yday

                # Calculate week number
                return (day_of_year + jan1_sunday_based - 1) // 7 + 1
            case _:
                # Default/Fallback (Unix standard)
                # %W: Week starts Monday. First week starting on Mon is Week 1.
                # Days before the first Monday are Week 0.
                return int(dt.strftime('%W'))

    def dates_diff(self, first_date: DateInput, second_date: DateInput, unit: Literal['seconds', 'minutes', 'hours', 'days'] = 'days'):
        ...

    def fiscal_year(self, date_input: DateInput, start_month: int = 4):
        ...

    def fiscal_month(self, date_input: DateInput, start_month: int = 4):
        ...

    def nth_working_day_of_month(self, n: int, date_input: DateInput, country_code: Optional[str] = None):
        ...

    def working_day_offset(self, days_offset: int, date_input: DateInput, country_code: Optional[str] = None):
        ...

    def _get_holiday_set(self, years: list[int], country_code: Optional[str]) -> set[date]:
        """
        Internal helper to retrieve a set of holiday dates for the specified years and country.

        Args:
            years (list[int]): A list of years for which to retrieve holidays.
            country_code (Optional[str]): The country code for which to retrieve holidays.

        Returns:
            set[date]: A set of holiday dates.

        """
        if not country_code:
            return set()
        holidays = set()
        for year in years:
            holidays.update(self.holiday_provider.get_holidays(year, country_code))
        return holidays

    def add_working_days(self, date_input: DateInput, days: int, country_code: Optional[str] = None) -> datetime:
        """
        Adds the specified number of working days to the given date.

        Args:
            date_input (DateInput): The date to add working days to.
            days (int): The number of working days to add.
            country_code (str): The country code in the format specified by the provider.
        """
        if days == 0:
            return self.normalize(date_input)

        dt = self.normalize(date_input)

        # Fetch holidays for relevant years to cover the range of `days`
        # A rough estimate: 200 working days per year. Add 2 for buffer.
        required_years = list(range(dt.year, dt.year + (days // 200) + 2))
        holidays = self._get_holiday_set(required_years, country_code)

        step = 1 if days > 0 else -1
        days_remaining = abs(days)
        current = dt

        while days_remaining > 0:
            current += timedelta(days=step)
            if current.weekday() < 5 and current.date() not in holidays:
                days_remaining -= 1
        return current

    def public_holidays(self, country_code: str, years: list[int]):
        ...

    def is_public_holiday(self, country_code: str, date_input: DateInput):
        ...