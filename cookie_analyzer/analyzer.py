from typing import TextIO, Iterator
from datetime import datetime, date

from .models import CookieLog, CookiesAnalysis, CookiesDataParser


class CSVFile:
    """Handles reading and parsing CSV file content.

     Constants:
         DATA_SEPARATOR: CSV delimiter (comma)
     """
    DATA_SEPARATOR = ","

    def __init__(self, file_stream: TextIO) -> None:
        file_stream.seek(0)
        self._file_stream = file_stream
        self._current_line_number = 0

    @staticmethod
    def extract_data_from_line(line: str) -> list[str]:
        """Split a CSV line into cleaned data elements.

        Args:
            line: CSV line

        Returns:
            List of whitespace-stripped data elements
        """
        return [
            data.strip() for data in line.split(CSVFile.DATA_SEPARATOR)
        ]

    def goto_beginning(self) -> None:
        """Reset file position to the beginning."""
        self._file_stream.seek(0)
        self._current_line_number = 0

    def get_headers(self) -> list[str]:
        """Extract header names from the CSV file.

        Returns:
            List of header names
        """
        self.goto_beginning()
        headers_line = self._file_stream.readline()
        self._current_line_number += 1

        return self.extract_data_from_line(headers_line)

    def iter_rows(self, skip_header: bool = True) -> Iterator[list[str]]:
        """Iterate through rows in the CSV file.

        Args:
            skip_header: Whether to skip the header row

        Yields:
            List of values for each row
        """
        self.goto_beginning()

        if skip_header:
            self._file_stream.readline()
            self._current_line_number += 1
        for line in self._file_stream:
            self._current_line_number += 1
            yield self.extract_data_from_line(line)


class CookiesAnalyzer(CSVFile):
    """Analyzes cookie log CSV files to find most active cookies.

    Constants:
        COOKIE_HEADER: Header name for cookie column
        TIMESTAMP_HEADER: Header name for timestamp column
    """
    COOKIE_HEADER = "cookie"
    TIMESTAMP_HEADER = "timestamp"

    def __init__(self, file_stream: TextIO) -> None:
        super().__init__(file_stream)
        self._data_parsers = self._init_data_parsers()

    def _cookie_parser(self, value: str) -> str:
        """Parse and validate a cookie value.

        Args:
            value: Cookie value to validate

        Returns:
            Validated cookie value

        Raises:
            ValueError: If cookie is empty
        """
        if len(value) == 0:
            raise ValueError(
                f"cookie is not correctly formatted on line {self._current_line_number}: '{value}'"
            )
        return value

    def _timestamp_parser(self, value: str) -> datetime:
        """Parse timestamp string to datetime object.

        Args:
            value: ISO-formatted timestamp string

        Returns:
            Parsed datetime object

        Raises:
            ValueError: If timestamp format is invalid
        """
        try:
            parsed_value = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(
                f"timestamp is not correctly formatted on line {self._current_line_number}: '{value}'"
            )
        return parsed_value

    def _init_data_parsers(self) -> list[CookiesDataParser]:
        """Create data parsers for each column based on headers.

        Returns:
            List of data parsers for supported columns

        Raises:
            ValueError: If an unsupported header is found
        """
        data_parsers: list[CookiesDataParser] = []
        headers_list = self.get_headers()

        for header in headers_list:
            if header == self.COOKIE_HEADER:
                data_parsers.append(
                    CookiesDataParser(
                        header_name=self.COOKIE_HEADER,
                        parsing_func=self._cookie_parser
                    )
                )
            elif header == self.TIMESTAMP_HEADER:
                data_parsers.append(
                    CookiesDataParser(
                        header_name=self.TIMESTAMP_HEADER,
                        parsing_func=self._timestamp_parser
                    )
                )
            else:
                raise ValueError(
                    f"unsupported header detected: '{header}'"
                )
        return data_parsers

    def _parse_cookie_log(self, row_data: list[str]) -> CookieLog:
        """Parse row data into a CookieLog object.

        Args:
            row_data: CSV row values

        Returns:
            CookieLog object with parsed data

        Raises:
            ValueError: If data is corrupt or column count mismatch
        """
        row_data_len = len(row_data)
        cookie_log = {}

        if row_data_len != len(self._data_parsers):
            raise ValueError(
                f"columns count is inconsistent on line {self._current_line_number}"
            )
        for i in range(row_data_len):
            value = row_data[i]
            data_parser = self._data_parsers[i]
            cookie_log[data_parser.header_name] = data_parser.parsing_func(
                value
            )
        return CookieLog(**cookie_log)

    def _get_cookies_analysis(
            self, target_date: date
    ) -> CookiesAnalysis:
        """Analyse cookie occurrences for the specified date.

        Args:
            target_date: Date to filter cookies by

        Returns:
            Analysis with cookie counts and maximum count
        """
        max_count = 0
        cookie_counts: dict[str, int] = {}

        for row_data in self.iter_rows(skip_header=True):
            cookie_log = self._parse_cookie_log(row_data)

            # Optimization: stop once we're past the target date
            if cookie_log.timestamp.date() < target_date:
                break
            if cookie_log.timestamp.date() == target_date:
                count = cookie_counts.get(cookie_log.cookie, 0) + 1
                cookie_counts[cookie_log.cookie] = count
                max_count = max(max_count, count)
        return CookiesAnalysis(
            cookies_count_map=cookie_counts,
            max_count=max_count
        )

    def get_most_active(self, target_date: date) -> list[str]:
        """Find cookies with highest occurrence count for a given date.

        Args:
            target_date: Date to filter cookies by

        Returns:
            List of cookie IDs with highest occurrence count
        """
        most_active = []
        cookies_analysis = self._get_cookies_analysis(target_date)

        for cookie, count in cookies_analysis.cookies_count_map.items():
            if count == cookies_analysis.max_count:
                most_active.append(cookie)
        return most_active
