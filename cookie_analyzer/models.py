from typing import Callable
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CookiesDataParser:
    """Configuration for parsing a specific column in a cookie log.

    Attributes:
        header_name: Column header name
        parsing_func: Function to convert string values to appropriate type
    """
    header_name: str
    parsing_func: Callable[[str], object]


@dataclass
class CookiesAnalysis:
    """Results of cookie count analysis.

    Attributes:
        cookies_count_map: Mapping of cookie IDs to occurrence counts
        max_count: Maximum occurrence count found
    """
    cookies_count_map: dict[str, int]
    max_count: int


@dataclass
class CookieLog:
    """A single cookie log entry.

    Attributes:
        cookie: Cookie identifier
        timestamp: When the cookie was recorded
    """
    cookie: str
    timestamp: datetime
