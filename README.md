# RPA_DATES
Python module delivers some actions to manipulate with dates and detect holidays.
The module is compatibile with the Robocorp.

## Installation
To install the package run:

```
pip install rpa_dates
```

## Example
### Fetching today's date
```
from rpa_dates import Dates
dates = Dates()
dates.today()
```
### Checking if today is a public holiday in Poland
```
from rpa_dates import Dates
dates = Dates()
dates.is_public_holiday('PL', )
```
### Get next business day from today's date including holidays for Peru
```
from rpa_dates import Dates
dates = Dates()
dates.next_working_day(include_holidays=True, country_code='PE')
```
### Dependencies
Python packages: calendar, typing, datetime, dateutil, requests
External: https://date.nager.at API
