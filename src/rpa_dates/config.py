from dataclasses import dataclass


@dataclass(frozen=True)
class DateConfig:
    """Holds configuration for date operations."""

    default_input_format: str = "%d.%m.%Y"
    default_output_format: str = "%d.%m.%Y"
    fiscal_year_start_month: int = 4
    api_timeout_seconds: int = 10
