"""
Test of rpa_dates package.
"""
from typing import Any
import unittest
import datetime
from rpa_dates import Dates

DATES: Dates = Dates()
DATE_FORMAT = '%d.%m.%Y'
TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
YESTERDAY = TODAY - datetime.timedelta(days=1)


class TestDates(unittest.TestCase):
    def test_new_date(self):
        test_value = DATES.new_date(11,1,2022)
        excpected_value = '11.01.2022'
        self.assertEqual(test_value, excpected_value)

    def test_change_date_format(self):
        test_value = DATES.change_date_format('11.01.2022', DATE_FORMAT, '%Y.%m.%d')
        excpected_value = '2022.01.11'
        self.assertEqual(test_value, excpected_value)

    def test_offset(self):
        test_value = DATES.offset('01.01.2022', days=1, date_format=DATE_FORMAT, output_format=DATE_FORMAT)
        excpected_value = '02.01.2022'
        self.assertEqual(test_value, excpected_value)

        test_value = DATES.offset('01.01.2022', days=-1, date_format=DATE_FORMAT, output_format=DATE_FORMAT)
        excpected_value = '31.12.2021'
        self.assertEqual(test_value, excpected_value)

        test_value = DATES.offset('2022-09-12 12:00:00', hours=1, date_format='%Y-%m-%d %H:%M:%S', output_format='%Y-%m-%d %H:%M:%S')
        excpected_value = '2022-09-12 13:00:00'
        self.assertEqual(test_value, excpected_value)

        test_value = DATES.offset('2022-09-12 12:00:00', minutes=15, date_format='%Y-%m-%d %H:%M:%S', output_format='%Y-%m-%d %H:%M:%S')
        excpected_value = '2022-09-12 12:15:00'
        self.assertEqual(test_value, excpected_value)

        test_value = DATES.offset('2022-09-12 12:00:00', seconds=-1, date_format='%Y-%m-%d %H:%M:%S', output_format='%Y-%m-%d %H:%M:%S')
        excpected_value = '2022-09-12 11:59:59'
        self.assertEqual(test_value, excpected_value)

    def test_today(self):
        test_value = DATES.today(DATE_FORMAT)
        excpected_value = TODAY.strftime(DATE_FORMAT)
        self.assertEqual(test_value, excpected_value)

    def test_yesterday(self):
        test_value = DATES.yesterday(DATE_FORMAT)
        excpected_value = YESTERDAY.strftime(DATE_FORMAT)
        self.assertEqual(test_value, excpected_value)

    def test_tomorrow(self):
        test_value = DATES.tomorrow(DATE_FORMAT)
        excpected_value = TOMORROW.strftime(DATE_FORMAT)
        self.assertEqual(test_value, excpected_value)

    def test_next_working_day(self):
        # Friday
        test_value = DATES.next_working_day('21.10.2022', '%d.%m.%Y')
        excpected_value = '24.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Saturday
        test_value = DATES.next_working_day('22.10.2022', '%d.%m.%Y')
        excpected_value = '24.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Sunday
        test_value = DATES.next_working_day('23.10.2022', '%d.%m.%Y')
        excpected_value = '24.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Monday
        test_value = DATES.next_working_day('24.10.2022', '%d.%m.%Y')
        excpected_value = '25.10.2022'
        self.assertEqual(test_value, excpected_value)

        # 1st day of Christmas - Sunday (next working day (Monday) is a public holiday)
        test_value = DATES.next_working_day('25.12.2022', '%d.%m.%Y', True, 'PL')
        excpected_value = '27.12.2022'
        self.assertEqual(test_value, excpected_value)

        # Wednesday (next two days are public holidays in Peru and then we have weekend)
        test_value = DATES.next_working_day('27.07.2022', '%d.%m.%Y', True, 'PE')
        excpected_value = '01.08.2022'
        self.assertEqual(test_value, excpected_value)

        # Friday (next working day (Monday) is a public holiday)
        test_value = DATES.next_working_day('23.12.2022', '%d.%m.%Y', True, 'PL')
        excpected_value = '27.12.2022'
        self.assertEqual(test_value, excpected_value)

        # Monday (next day (Tuesday) is a public holiday)
        test_value = DATES.next_working_day('31.10.2022', '%d.%m.%Y', True, 'PL')
        excpected_value = '02.11.2022'
        self.assertEqual(test_value, excpected_value)

    def test_previous_working_day(self):
        # Sunday
        test_value = DATES.previous_working_day('23.10.2022', '%d.%m.%Y')
        excpected_value = '21.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Saturday
        test_value = DATES.previous_working_day('22.10.2022', '%d.%m.%Y')
        excpected_value = '21.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Friday
        test_value = DATES.previous_working_day('21.10.2022', '%d.%m.%Y')
        excpected_value = '20.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Monday
        test_value = DATES.previous_working_day('24.10.2022', '%d.%m.%Y')
        excpected_value = '21.10.2022'
        self.assertEqual(test_value, excpected_value)

        # Monday (previous working day (Friday) is a public holiday)
        test_value = DATES.previous_working_day('14.11.2022', '%d.%m.%Y', True, 'PL')
        excpected_value = '10.11.2022'
        self.assertEqual(test_value, excpected_value)

        # Two previous days are public holidays
        test_value = DATES.previous_working_day('01.08.2022', '%d.%m.%Y', True, 'PE')
        excpected_value = '27.07.2022'
        self.assertEqual(test_value, excpected_value)

        # Previous day is a public holiday
        test_value = DATES.previous_working_day('02.11.2022', '%d.%m.%Y', True, 'PL')
        excpected_value = '31.10.2022'
        self.assertEqual(test_value, excpected_value)

    def test_first_day_of_month(self):
        test_value = DATES.first_day_of_month('12.04.2022', DATE_FORMAT, DATE_FORMAT)
        excpected_value = '01.04.2022'
        self.assertEqual(test_value, excpected_value)

    def test_last_day_of_month(self):
        test_value = DATES.last_day_of_month('12.04.2022', DATE_FORMAT, DATE_FORMAT)
        excpected_value = '30.04.2022'
        self.assertEqual(test_value, excpected_value)

    def test_calculate_date_of_day_of_week(self):
        test_value = DATES.calculate_date_of_weekday('21.10.2022', DATE_FORMAT, 'mon')
        excpected_value = '17.10.2022'
        self.assertEqual(test_value, excpected_value)

    def test_day_of_year(self):
        test_value = DATES.day_of_year('05.01.2022', DATE_FORMAT)
        excepcted_value = 5
        self.assertEqual(test_value, excepcted_value)

    def test_week_of_year(self):
        test_dates: list[dict[str, Any]] = [
            { 'value': '01.01.2014', 'excpected': 1, 'iso': True },
            { 'value': '01.01.2022', 'excpected': 52, 'iso': True },
            { 'value': '01.01.2027', 'excpected': 53, 'iso': True },
            { 'value': '12.03.2029', 'excpected': 11, 'iso': True },
            { 'value': '23.10.2022', 'excpected': 42, 'iso': True },
            { 'value': '01.01.2014', 'excpected': 1, 'iso': False },
            { 'value': '01.01.2022', 'excpected': 1, 'iso': False },
            { 'value': '01.01.2027', 'excpected': 1, 'iso': False },
            { 'value': '12.03.2029', 'excpected': 11, 'iso': False },
            { 'value': '23.10.2022', 'excpected': 43, 'iso': False }
        ]

        for date in test_dates:
            self.assertEqual(DATES.week_of_year(date['value'], DATE_FORMAT, date['iso']), date['excpected'])

    def test_difference_between_dates_in_days(self):
        test_value = DATES.difference_between_dates(TOMORROW.strftime(DATE_FORMAT), YESTERDAY.strftime(DATE_FORMAT), DATE_FORMAT, 'days')
        excepcted_value = 2
        self.assertEqual(test_value, excepcted_value)

    def test_get_fiscal_year(self):
        test_value = DATES.get_fiscal_year('12.04.2022', DATE_FORMAT, 4)
        excpected_value = 2023
        self.assertEqual(test_value, excpected_value)

    def test_get_fiscal_month(self):
        test_value = DATES.get_fiscal_month('12.04.2022', DATE_FORMAT, 4)
        excpected_value = 1
        self.assertEqual(test_value, excpected_value)

    def test_get_holidays(self):
        test_value = DATES.get_public_holidays('PL', 2022)
        excpected_value = ['2022-01-01', '2022-01-06', '2022-04-17', '2022-04-18', '2022-05-01', '2022-05-03', '2022-06-05', '2022-06-16', '2022-08-15', '2022-11-01', '2022-11-11', '2022-12-25', '2022-12-26']
        self.assertEqual(test_value, excpected_value)
    
    def test_is_holiday(self):
        test_value: bool = DATES.is_public_holiday('PL', '10.10.2022', DATE_FORMAT)
        excpected_value = False
        self.assertEqual(test_value, excpected_value)

        test_value = DATES.is_public_holiday('PL', '01.05.2022', DATE_FORMAT)
        excpected_value = True
        self.assertEqual(test_value, excpected_value)

        test_value = DATES.is_public_holiday('PL')
        excpected_value = False
        self.assertEqual(test_value, excpected_value)
        

if __name__ == '__main__':
    unittest.main()