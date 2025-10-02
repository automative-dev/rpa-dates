# rpa-dates

A straightforward and powerful Python utility library for common date and time operations, especially useful in RPA (Robotic Process Automation) and general scripting.

## Key Features

* **Date Manipulation**: Easily add or subtract days, months, and years.  
* **Business Day Calculations**: Find the next/previous working day, the nth working day of a month, or offset by a number of business days.  
* **Public Holiday Integration**: Fetch public holidays for any country and factor them into business day calculations.  
* **Date Information**: Get the first/last day of the month, week/day of the year, fiscal periods, and more.  
* **Flexible Inputs/Outputs**: Accepts strings, date, and datetime objects. Returns formatted strings or datetime objects.  
* **Time Differences**: Calculate the difference between two dates in days, hours, minutes, or seconds.

## Installation

Install the package from PyPI using pip:  

```bash
pip install rpa-dates
```

## Quickstart & Usage Examples

All methods are available as static methods on the Dates class.

### Basic Setup

```Python
from rpa_dates import Dates  
from datetime import date
```

> All methods are static, no need to instantiate the class.

### Date Offsetting

Easily add or subtract time from any given date. If no date is provided, it defaults to today.  

```Python
# Get the date 3 months and 15 days from now
future_date = Dates.offset(date_input=None, months=3, days=15)  
print(f"In 3 months and 15 days: {future_date}")

# Get the date 2 years ago from a specific date  
past_date = Dates.offset(date_input="15.07.2024", years=-2, format='datetime')  
print(f"Two years before 15.07.2024: {past_date.strftime('%d-%m-%Y')}")
```

### Working with Business Days (including Holidays)

The library can skip weekends and public holidays. It uses the [Nager.Date API](https://date.nager.at) for holiday data.  

```Python
# Find the next working day in Poland, skipping weekends and public holidays  
# Assuming "10.11.2023" is a Friday. Next working day would be Monday 13.11.2023  
next_business_day = Dates.next_working_day(date_input="10.11.2023", country_code="PL")  
print(f"Next working day in Poland after 10.11.2023 is: {next_business_day}")

# Find the 10th working day of the current month  
tenth_working_day = Dates.nth_working_day_of_month(n=10)  
print(f"10th working day of this month: {tenth_working_day}")

# Find the date 5 working days from today  
future_working_day = Dates.working_day_offset(days_offset=5)  
print(f"5 working days from now: {future_working_day}")
```

### Month and Week Calculations

```Python
# Get the first and last day of the current month  
first_day = Dates.first_day_of_month()  
last_day = Dates.last_day_of_month()  
print(f"This month runs from {first_day} to {last_day}")

# What date is Friday of the week containing "18.03.2024" (a Monday)?  
friday_date = Dates.calculate_date_of_weekday(date_input="18.03.2024", week_day='fri')  
print(f"Friday of that week is: {friday_date}")
```

### Date Information and Differences

```Python
# Get the day and week number of the year  
day_num = Dates.day_of_year()  
week_num = Dates.week_of_year()  
print(f"Today is day number {day_num} in week {week_num} of the year.")

# Calculate the difference in hours between two dates  
diff_hours = Dates.difference_between_dates(  
    first_date="01.01.2024 10:00:00",  
    second_date="02.01.2024 12:00:00",  
    date_format='%d.%m.%Y %H:%M:%S',  
    unit='hours'  
)  
print(f"Difference is {diff_hours} hours.")
```

## API Reference

The Dates class provides a comprehensive set of static methods for date operations.

| Method | Description |
| :---- | :---- |
| new\_datetime() | Creates a new date object from individual components (year, month, day, etc.). |
| convert\_to\_datetime() | Converts a date string to a datetime object. |
| change\_date\_format() | Converts a date string from one format to another. |
| offset() | Applies an offset of days, months, or years to a date. |
| today() | Returns today's date. |
| yesterday() | Returns yesterday's date. |
| tomorrow() | Returns tomorrow's date. |
| next\_working\_day() | Finds the next business day, skipping weekends and optional holidays. |
| previous\_working\_day() | Finds the previous business day, skipping weekends and optional holidays. |
| first\_day\_of\_month() | Returns the first day of the month for a given date. |
| last\_day\_of\_month() | Returns the last day of the month for a given date. |
| calculate\_date\_of\_weekday() | Finds the date of a specific weekday (e.g., 'fri') within the same week. |
| day\_of\_year() | Returns the day number of the year (1-366). |
| week\_of\_year() | Returns the week number of the year. |
| difference\_between\_dates() | Calculates the absolute difference between two dates in a specified unit. |
| get\_fiscal\_year() | Calculates the fiscal year based on a custom start month. |
| get\_fiscal\_month() | Calculates the fiscal month based on a custom start month. |
| get\_public\_holidays() | Fetches public holidays for a given country and year. |
| is\_public\_holiday() | Checks if a specific date is a public holiday. |
| nth\_working\_day\_of\_month() | Finds the Nth working day of a given month. |
| working\_day\_offset() | Calculates a new date by adding or subtracting a number of working days. |

## **Dependencies**

* [python-dateutil](https://pypi.org/project/python-dateutil/)  
* [requests](https://pypi.org/project/requests/)

## **Contributing**

Contributions, issues, and feature requests are welcome\! Please feel free to check the [issues page](https://github.com/21010/automative-dev/issues).

## **License**

This project is licensed under the MIT License. See the LICENSE file for details.