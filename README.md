# RPA Dates 2.0

**A robust, fault-tolerant Python library for date calculations in Robotic Process Automation (RPA).**

`rpa-dates` simplifies complex date arithmetic—especially regarding working days and holidays—ensuring your automation bots never crash due to unexpected calendar edge cases or API outages.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Build Status](https://github.com/21010/rpa-dates/actions/workflows/ci.yml/badge.svg)](https://github.com/21010/rpa-dates/actions/workflows/ci.yml)

## Key Features

* **Resilient Holiday Fetching**: Uses a "Chain of Responsibility" fallback strategy.
    1.  **Local Library** (0ms latency, works offline).
    2.  **Nager.Date API** (Primary Web API).
    3.  **OpenHolidays API** (Backup Web API).
    * *If one fails, the next one takes over automatically.*
* **Production-Grade Working Day Logic**:
    * Correctly handles **year boundaries** (e.g., adding 5 working days to Dec 29th).
    * Preserves time components (e.g., `14:30` remains `14:30`).
    * Supports positive and negative offsets.
* **RPA-Friendly**: Designed to handle string, `date`, and `datetime` inputs interchangeably.
* **Fiscal Year Support**: Built-in utilities for fiscal calendars.

## Installation

Install using `uv` (recommended) or `pip`:

```bash
uv add rpa-dates
# OR
pip install rpa-dates
```

## Quick Start

### Basic Date Operations

The DateService accepts `strings`, `dates`, or `datetimes` and normalizes them automatically.

```python
from rpa_dates import DateService

ds = DateService()

# Normalizes inputs automatically
dt = ds.normalize("11.02.2025")  # Returns datetime object

# Easy offsets
future_date = ds.offset("01.01.2025", days=10, months=1)
print(future_date)  # 11.02.2025
```

### Working with Business Days

Calculate deadlines accurately by skipping weekends and public holidays.

```python
# Calculate +5 working days from a Friday
# Skips Sat, Sun, and any public holidays found for the country (e.g., 'US')
deadline = ds.working_day_offset(5, "2025-07-03", country_code="US")

print(deadline)
# If July 4th is a holiday, this correctly skips it!
```

### Finding the Nth Working Day

Perfect for "Report is due on the 3rd working day of the month" scenarios.

```python
# Get the 3rd working day of January 2025 in Poland (PL)
report_date = ds.nth_working_day_of_month(3, "2025-01-01", country_code="PL")

print(report_date)
# 2025-01-01 is New Year (Holiday) -> Skip
# 2025-01-02 (Thu) -> 1st WD
# 2025-01-03 (Fri) -> 2nd WD
# 2025-01-04 (Sat) -> Skip
# 2025-01-05 (Sun) -> Skip
# 2025-01-06 (Mon) is Epiphany (Holiday) -> Skip
# 2025-01-07 (Tue) -> 3rd WD (Result)
```

## Configuration

You can customize the service behavior using DateConfig.

```python
from rpa_dates import DateService, DateConfig

config = DateConfig(
    default_input_format='%Y-%m-%d',
    fiscal_year_start_month=10,  # e.g., US Government fiscal year
    api_timeout_seconds=5
)

ds = DateService(config=config)
```

## Architecture: The Provider Fallback

The library guarantees high availability for holiday data using a multi-provider strategy.

* LocalPythonHolidayProvider: Checks the local holidays Python package. Fast and offline.
* NagerDateV3Provider: Queries date.nager.at.
* NagerDateV4Provider: Queries the newer V4 API.
* OpenHolidaysProvider: Queries openholidaysapi.org.

You don't need to configure this; it happens automatically inside ProviderFactory.

## Contributing

I use `uv` for dependency management.

1. Clone the repo:
    ```bash
    git clone [https://github.com/21010/rpa-dates.git](https://github.com/21010/rpa-dates.git)
    cd rpa-dates
    ```
   
2. Install dependencies:
    ```bash
    uv sync
    ```
   
3. Run Tests:
    ```bash
    uv run pytest
    ```
## License

This project is licensed under the MIT License - see the LICENSE file for details.