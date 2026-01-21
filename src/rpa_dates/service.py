import calendar
from functools import lru_cache

from datetime import datetime, date, timedelta
from typing import Optional, Literal
from dateutil.relativedelta import relativedelta

from .config import DateConfig
from .interfaces import HolidayProvider
from .factories import ProviderFactory
from .exceptions import DateOperationError


DateInput = str | date | datetime


class DateService:
    WEEK_DAYS = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}

    def __init__(self, config: Optional[DateConfig] = None, holiday_provider: Optional[HolidayProvider] = None):
        self.config = config or DateConfig()
        self.holiday_provider = holiday_provider or ProviderFactory.create_provider(self.config.api_timeout_seconds)

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
            input_format = input_format or self.config.default_input_format
            try:
                return datetime.strptime(date_input, input_format)
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

    def first_day_of_month(self, date_input: DateInput) -> datetime:
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

    def dates_diff(self, first_date: DateInput, second_date: DateInput, unit: Literal['seconds', 'minutes', 'hours', 'days'] = 'days') -> int | float:
        """
        Calculates the absolute difference between two dates in the specified unit.

        Args:
            first_date (DateInput): The first date.
            second_date (DateInput): The second date.
            unit (Literal['seconds', 'minutes', 'hours', 'days']): The unit to calculate the difference in.

        Returns:
            int | float: The absolute difference between the two dates in the specified unit.
        """
        dt1 = self.normalize(first_date)
        dt2 = self.normalize(second_date)

        diff = abs(dt1 - dt2)

        match unit:
            case 'hours':
                return diff.total_seconds() / 3600
            case 'minutes':
                return diff.total_seconds() / 60
            case 'seconds':
                return diff.total_seconds()
            case _:
                return diff.days

    def fiscal_year(self, date_input: DateInput, start_month: int = 4) -> int:
        """
        Return the fiscal year for given date.

        Args:
            date_input (DateInput): The date to get the fiscal year for.
            start_month (int): The month in which the fiscal year starts. Defaults to 4.

        Returns:
            int: The fiscal year for the given date.
        """
        dt = self.normalize(date_input)
        return dt.year if dt.month < start_month else dt.year + 1

    def fiscal_month(self, date_input: DateInput, start_month: int = 4) -> int:
        """
        Return the fiscal month for given date.

        Args:
            date_input (DateInput): The date to get the fiscal month for.
            start_month (int): The month in which the fiscal year starts. Defaults to 4.

        Returns:
            int: The fiscal month for the given date.
        """
        dt = self.normalize(date_input)
        return (dt.month - start_month + 12) % 12 + 1

    def nth_working_day_of_month(self, n: int, date_input: DateInput, country_code: Optional[str] = None) -> datetime:
        """
        Returns the nth working day of the month.

        Args:
            n (int): The day number.
            date_input (DateInput): The date to get the nth working day for.
            country_code (Optional[str]): The country code for which to get the nth working day for.

        Returns:
            datetime: The nth working day of the month.
        """
        # Validate input parameters
        if n <= 0:
            raise ValueError("Day 'n' must be a positive integer.")

        # Get a list of working days in the month
        working_days = self.get_working_days_in_month(date_input, country_code)

        # Check if there are enough working days in the month for the requested day number
        if n > len(working_days):
            raise ValueError(f"Month has fewer than {n} working days.")

        # Return the nth working day of the month
        return working_days[n - 1]

    def working_day_offset(self, days_offset: int, date_input: DateInput, country_code: Optional[str] = None) -> datetime:
        """
        Calculates a date by offsetting a number of working days.

        Args:
            days_offset (int): The number of working days to offset.
            date_input (DateInput): The date to offset.
            country_code: Optional[str] = None

        Returns:
            datetime: The new datetime object after applying the offset.
        """
        dt = self.normalize(date_input)

        # Return immediately for 0 offset
        if days_offset == 0:
            return dt

        step = 1 if days_offset > 0 else -1
        days_remaining = abs(days_offset)

        # Initialize the current date to the input date
        current = dt

        # Track the currently loaded holiday year to avoid re-fetching unnecessarily
        def get_comp_date(d: DateInput):
            return d.date() if isinstance(d, datetime) else d

        current_comp_date = get_comp_date(current)
        loaded_year = current_comp_date.year

        # Load initial holidays
        holidays = self._get_holiday_set((loaded_year,), country_code) if country_code else set()

        while days_remaining > 0:
            current += timedelta(days=step)
            check_date = get_comp_date(current)

            # If we crossed into a new year, update the holiday set
            if country_code and check_date.year != loaded_year:
                loaded_year = check_date.year
                holidays = self._get_holiday_set((loaded_year,), country_code)

            # Check: Weekday (0-4) AND not a holiday
            if check_date.weekday() < 5 and (not country_code or check_date not in holidays):
                days_remaining -= 1

        return current

    def get_working_days_in_month(self, date_input: DateInput, country_code: Optional[str] = None) -> list[datetime]:
        """
        Returns a list of working days in the month.

        Args:
            date_input (DateInput): The date to get the working days for.
            country_code (Optional[str]): The country code for which to get the working days for.

        Returns:
            list[datetime]: A list of working days in the month.
        """
        # Normalize the date
        dt = self.normalize(date_input)

        # Fetch holidays for relevant years to cover the range of `days`
        holidays = self._get_holiday_set((dt.year,), country_code) if country_code else set()

        # Get the number of days in the month
        _, days_in_month = calendar.monthrange(dt.year, dt.month)

        # Create a list of all days in the month
        all_days = (dt.replace(day=day) for day in range(1, days_in_month + 1))

        # Filter out weekends and holidays from the list of all days in the month
        working_days = [day for day in all_days if day.weekday() < 5 and day.date() not in holidays]

        return working_days

    @lru_cache(maxsize=32)
    def _get_holiday_set(self, years: tuple[int], country_code: Optional[str]) -> set[date]:
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

    def public_holidays(self, years: list[int], country_code: str) -> set[date]:
        """
        Return holidays for given year and country. Results are cached.
        List of countries: https://date.nager.at/Country

        Args:
            country_code (str): The country code in the format specified by the provider.
            years (list[int]): A list of years

        Returns:
            set[date]: A set of holiday dates.
        """
        return self._get_holiday_set(tuple(years), country_code)

    def is_public_holiday(self, date_input: DateInput, country_code: str) -> bool:
        """
        Check if a given date is a public holiday in the specified country.

        Args:
            date_input (DateInput): The date to check.
            country_code (str): The country code in the format specified by the provider.

        Returns:
            bool: True if the date is a public holiday, False otherwise.
        """
        dt = self.normalize(date_input)
        holidays = self._get_holiday_set((dt.year,), country_code)
        return dt.date() in holidays
