""" Delivers methods to operate with dates and times objects. """

import calendar
from typing import Literal
import datetime
from dateutil.relativedelta import relativedelta
import requests

class Dates:
    """ Delivers methods to operate with dates and times objects. """
    def __init__(self) -> None:
        self._date: datetime.datetime = datetime.date.today()
        self.week_days: dict[str, int] = { 'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6 }

    def new_date(self, day: int, month: int, year: int, output_format: str = '%d.%m.%Y') -> str:
        """
        Return new date in given format (default: %d.%m.%Y)

        Args:
            day (int): day of month (1 - 31)
            month (int): month of year (1 - 12)
            year (int): year
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: TypeError, ValueError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            return datetime.date(year, month, day).strftime(output_format)
        except (TypeError, ValueError) as ex:
            raise Exception from ex

    def change_date_format(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', output_format: str = '%d.%m.%Y') -> str:
        """
        Convert the date from one format to another (default: %d.%m.%Y)

        Args:
            date_string (str): date string, ex. 12.12.2022
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            return _date.strftime(output_format)
        except (TypeError, ValueError) as ex:
            raise Exception from ex

    def offset(self, date_string: str | None = None, date_format:str = '%d.%m.%Y', seconds: int | None = None, minutes: int | None = None, hours: int | None = None, days: int | None = None, output_format: str = '%d.%m.%Y') -> str:
        """_summary_

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            seconds (int | None, optional): positive or negative value of the offset. Defaults to None.
            minutes (int | None, optional): positive or negative value of the offset. Defaults to None.
            hours (int | None, optional): positive or negative value of the offset. Defaults to None.
            days (int | None, optional): positive or negative value of the offset. Defaults to None.
            months (int | None, optional): positive or negative value of the offset. Defaults to None.
            years (int | None, optional): positive or negative value of the offset. Defaults to None.
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: NameError, ValueError, TypeError, OverflowError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)

            if seconds is not None:
                _date += datetime.timedelta(seconds=seconds)
            if minutes is not None:
                _date += datetime.timedelta(minutes=minutes)
            if hours is not None:
                _date += datetime.timedelta(hours=hours)
            if days is not None:
                _date += datetime.timedelta(days=days)

            return _date.strftime(output_format)
        except (NameError, ValueError, TypeError, OverflowError) as ex:
            raise Exception from ex

    def today(self, output_format='%d.%m.%Y') -> str:
        """
        Returns today's date in given string format (%d.%m.%Y as default)

        Args:
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: TypeError, NameError, ValueError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            return self._date.today().strftime(output_format)
        except (TypeError, NameError, ValueError) as ex:
            raise Exception from ex

    def yesterday(self, output_format='%d.%m.%Y') -> str:
        """
        Returns yesterday's date in given string format (%d.%m.%Y as default)

        Args:
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: TypeError, NameError, ValueError

        Returns:
            str: date string in given format
        """
        try:
            return (self._date.today() - datetime.timedelta(days=1)).strftime(output_format)
        except (TypeError, NameError, ValueError) as ex:
            raise Exception from ex

    def tomorrow(self, output_format='%d.%m.%Y') -> str:
        """
        Returns tomorrow's date in given string format (%d.%m.%Y as default)

        Args:
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: TypeError, NameError, ValueError

        Returns:
            str: date string in given format
        """
        try:
            return (self._date.today() + datetime.timedelta(days=1)).strftime(output_format)
        except (TypeError, NameError, ValueError) as ex:
            raise Exception from ex

    def next_working_day(self, date_string: str | None = None, date_format:str = '%d.%m.%Y', include_holidays: bool = False, country_code: str | None = None, output_format: str = '%d.%m.%Y') -> str:
        """
        Returns date (str) of next working day (ommitting weekends and holidays if included)

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            include_holidays (bool, optional): determines if holidays should be included or not. Defaults to False.
            country_code (str | None, optional): country code ex. 'PL'. Full list available here: https://date.nager.at/Country. Defaults to None.
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: Exceptions from Holidays API if used and TypeError, NameError, ValueError, OverflowError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)

            if _date.weekday() == 4: # Friday
                _date += datetime.timedelta(days=3)
            elif _date.weekday() == 5: # Saturday
                _date += datetime.timedelta(days=2)
            else: # Rest of days
                _date += datetime.timedelta(days=1)

            if include_holidays is True and country_code is not None:
                while self.is_public_holiday(country_code, _date.strftime(date_format), date_format) is True:
                    _date += datetime.timedelta(days=1)
                    if _date.weekday() == 5:
                        _date += datetime.timedelta(days=2)
                    elif _date.weekday() == 6:
                        _date += datetime.timedelta(days=1)
            elif include_holidays is True and country_code is None:
                raise Exception('invalid country_code')

            return _date.strftime(output_format)
        except Exception as ex:
            raise Exception from ex

    def previous_working_day(self, date_string: str | None = None, date_format:str = '%d.%m.%Y', include_holidays: bool = False, country_code: str | None = None, output_format: str = '%d.%m.%Y') -> str:
        """
        Returns date (str) of previous working day (ommitting weekends and holidays if included)

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            include_holidays (bool, optional): determines if holidays should be included or not. Defaults to False.
            country_code (str | None, optional): country code ex. 'PL'. Full list available here: https://date.nager.at/Country. Defaults to None.
            output_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: Exceptions from Holidays API if used and TypeError, NameError, ValueError, OverflowError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)

            if _date.weekday() == 0: # Monday
                _date = _date - datetime.timedelta(days=3)
            elif _date.weekday() == 6: # Sunday
                _date = _date - datetime.timedelta(days=2)
            else: # Rest of days
                _date = _date - datetime.timedelta(days=1)

            if include_holidays is True and country_code is not None:
                while self.is_public_holiday(country_code, _date.strftime(date_format), date_format) is True:
                    _date -= datetime.timedelta(days=1)
                    if _date.weekday() == 6:
                        _date -= datetime.timedelta(days=2)
                    elif _date.weekday() == 5:
                        _date -= datetime.timedelta(days=1)

            return _date.strftime(output_format)
        except Exception as ex:
            raise Exception from ex

    def first_day_of_month(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', output_format="%d.%m.%Y") -> str:
        """
        Returns the first day of month for given string date in given string format (%d.%m.%Y as default)

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            output_format (str, optional): pythonic date format. Defaults to "%d.%m.%Y".

        Raises:
            Exception: TypeError, NameError, ValueError, OverflowError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            return _date.replace(day=1).strftime(output_format)
        except (TypeError, NameError, ValueError, OverflowError) as ex:
            raise Exception from ex

    def last_day_of_month(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', output_format="%d.%m.%Y") -> str:
        """
        Returns the last day of month for given string date in given string format (%d.%m.%Y as default)

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            output_format (str, optional): pythonic date format. Defaults to "%d.%m.%Y".

        Raises:
            Exception: TypeError, NameError, ValueError, OverflowError

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            return _date.replace(day=calendar.monthrange(_date.year, _date.month)[1]).strftime(output_format)
        except (TypeError, NameError, ValueError) as ex:
            raise Exception from ex

    def calculate_date_of_weekday(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', week_day: Literal['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] = 'mon', output_format="%d.%m.%Y") -> str:
        """
        Return the date of the week day from the week for given date in given output format (default (%d.%m.%Y))

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            week_day (Literal['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], optional): weekday. Defaults to 'mon'.
            output_format (str, optional): pythonic date format. Defaults to "%d.%m.%Y".

        Raises:
            Exception: TypeError, NameError, ValueError, OverflowError, Generic Exception

        Returns:
            str: date string in given format

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            monday: datetime.datetime = _date - datetime.timedelta(days=_date.weekday())
            res: datetime.datetime = monday + datetime.timedelta(days=self.week_days[week_day])
            return res.strftime(output_format)
        except Exception as ex:
            raise Exception from ex

    def day_of_year(self, date_string: str | None = None, date_format: str = '%d.%m.%Y') -> int:
        """
        Returns the day of year.

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: NameError, ValueError, TypeError, Generic Eror

        Returns:
            int: number value of the day of year

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = datetime.datetime.strptime(date_string, date_format)
            return int(_date.strftime('%j'))
        except Exception as ex:
            raise Exception from ex

    def week_of_year(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', iso_format: bool = True) -> int:
        """
        Returns the number of the week in ISO 8601 or non-ISO standard.

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            iso_format (bool, optional): pythonic date format. Defaults to True.

        Raises:
            Exception: NameError, ValueError, TypeError, Generic Eror

        Returns:
            int: number value of week of the year

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            match iso_format:
                case True:
                    return(int(date.isocalendar().week))
                case False:
                    return int((date - date.replace(month=1, day=1)).days / 7) + 1
        except Exception as ex:
            raise Exception from ex

    def difference_between_dates(self, first_date_string: str, second_date_string: str, date_format: str = '%d.%m.%Y', unit: Literal['seconds', 'minutes', 'hours', 'days'] = 'days') -> int:
        """
        Return the difference between two dates in given unit

        Args:
            first_date_string (str): date string of the first date
            second_date_string (str): date string of the second date
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            unit (Literal['seconds', 'minutes', 'hours', 'days'], optional): measure unit. Defaults to 'days'.

        Raises:
            Exception: TypeError, NameError, ValueError, Generic Error

        Returns:
            int: number value of the difference in selected unit (ex. days)

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date1: datetime.datetime = self.__to_datetime__(first_date_string, date_format)
            _date2: datetime.datetime = self.__to_datetime__(second_date_string, date_format)
            diff: datetime.timedelta = _date1 - _date2

            match unit:
                case 'seconds':
                    return abs(diff.seconds)
                case 'minutes':
                    return abs(diff.min)
                case 'hours':
                    return abs(diff.min) / 60
                case 'days':
                    return abs(diff.days)
        except Exception as ex:
            raise Exception from ex

    def get_fiscal_year(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', start_month_of_fiscal_year: int = 4) -> int:
        """
        Return the fiscal year for given date

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            start_month_of_fiscal_year (int, optional): the number value of the first month of fiscal year. Defaults to 4.

        Raises:
            Exception: ValueError, NameError, TypeError

        Returns:
            int: number value of the fiscal year

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            return _date.year if _date.month < start_month_of_fiscal_year else _date.year + 1
        except Exception as ex:
            raise Exception from ex

    def get_fiscal_month(self, date_string: str | None = None, date_format: str = '%d.%m.%Y', start_month_of_fiscal_year: int = 4) -> int:
        """
        Return the fiscal month for given date

        Args:
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.
            start_month_of_fiscal_year (int, optional): the number value of the first month of fiscal year. Defaults to 4.

        Raises:
            Exception: ValueError, NameError, TypeError

        Returns:
            int: number value of the fiscal month

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        try:
            _date: datetime.datetime = self.__to_datetime__(date_string, date_format)
            return (_date - relativedelta(months=start_month_of_fiscal_year-1)).month
        except Exception as ex:
            raise Exception from ex

    def get_public_holidays(self, country_code: str, year: int, dates_only: bool = True) -> dict | list:
        """
        Return holidays for given year and given country.
        Use https://date.nager.at API
        List of countries: https://date.nager.at/Country

        Args:
            country_code (str): country code, ex. PL
            year (int): number value of the year
            dates_only (bool, optional): determines if results should contains only dates (list). Defaults to True.

        Raises:
            Exception: ValueError, NameError, TypeError

        Returns:
            dict | list: all holidays for the given country and the year
        """
        try:
            url: str = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}'
            response: requests.Response = requests.get(url)
            if response.status_code == 200:
                holidays: dict = {item['date']: item['name'] for item in response.json()}
                return list(holidays.keys()) if dates_only is True else holidays
        except requests.RequestException as ex:
            raise Exception from ex

    def is_public_holiday(self, country_code: str, date_string: str | None = None, date_format: str = '%d.%m.%Y') -> bool:
        """
        Check if given date is public holiday in given country.\n\r
        Use https://date.nager.at API\n\r
        List of countries: https://date.nager.at/Country\n\r

        Args:
            country_code (str): country code, ex. PL
            date_string (str | None, optional): date string. Defaults to None.
            date_format (str, optional): pythonic date format. Defaults to '%d.%m.%Y'.

        Raises:
            Exception: NameError, ValueError, TypeError, requests.RequestException

        Returns:
            bool: True if the date is holiday, False if not

        More about date formats:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        if date_string is None:
            year: int = datetime.datetime.today().year
        elif isinstance(date_string, str):
            try:
                year = datetime.datetime.strptime(date_string, date_format).year
            except ValueError as ex:
                raise Exception from ex

        url: str = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}'
        response: requests.Response = requests.get(url)
        if response.status_code != 200:
            raise requests.RequestException

        holidays: list = [self.change_date_format(item['date'], '%Y-%m-%d', date_format) for item in response.json()]
        return date_string in holidays

    def __to_datetime__(self, date_string: str | None = None, date_format: str = '%d.%m.%Y') -> str:
        if date_string is None:
            return datetime.datetime.today()
        return datetime.datetime.strptime(date_string, date_format)
