import io
import unittest
from datetime import datetime, date

from cookie_analyzer.analyzer import CSVFile, CookiesAnalyzer


class TestCSVFile(unittest.TestCase):
    def test_extract_data_from_line(self):
        line = "value1, value2 ,value3"
        expected = ["value1", "value2", "value3"]
        self.assertEqual(CSVFile.extract_data_from_line(line), expected)

    def test_get_headers(self):
        file_content = "header1,header2,header3\nvalue1,value2,value3"
        file_stream = io.StringIO(file_content)
        csv_file = CSVFile(file_stream)

        self.assertEqual(
            csv_file.get_headers(),
            ["header1", "header2", "header3"]
        )

    def test_iter_rows(self):
        file_content = "header1,header2\nvalue1,value2\nvalue3,value4"
        file_stream = io.StringIO(file_content)
        csv_file = CSVFile(file_stream)

        rows = list(csv_file.iter_rows())
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["value1", "value2"])
        self.assertEqual(rows[1], ["value3", "value4"])


class TestCookiesAnalyzer(unittest.TestCase):
    def setUp(self):
        # Sample cookie log data
        self.log_data = (
            "cookie,timestamp\n"
            "cookie1,2021-12-09T14:19:00+00:00\n"
            "cookie2,2021-12-09T10:13:00+00:00\n"
            "cookie1,2021-12-09T07:25:00+00:00\n"
            "cookie3,2021-12-08T22:03:00+00:00\n"
            "cookie1,2021-12-07T23:30:00+00:00\n"
        )
        self.file_stream = io.StringIO(self.log_data)
        self.analyzer = CookiesAnalyzer(self.file_stream)

    def test_cookie_parser(self):
        self.assertEqual(self.analyzer._cookie_parser("test_cookie"), "test_cookie")

        with self.assertRaises(ValueError):
            self.analyzer._cookie_parser("")

    def test_timestamp_parser(self):
        timestamp = "2021-12-09T14:19:00+00:00"
        expected = datetime.fromisoformat(timestamp)
        self.assertEqual(self.analyzer._timestamp_parser(timestamp), expected)

        with self.assertRaises(ValueError):
            self.analyzer._timestamp_parser("invalid-timestamp")

    def test_init_data_parsers(self):
        parsers = self.analyzer._data_parsers
        self.assertEqual(len(parsers), 2)
        self.assertEqual(parsers[0].header_name, "cookie")
        self.assertEqual(parsers[1].header_name, "timestamp")

    def test_parse_cookie_log(self):
        log = self.analyzer._parse_cookie_log(["cookie1", "2021-12-09T14:19:00+00:00"])
        self.assertEqual(log.cookie, "cookie1")
        self.assertEqual(
            log.timestamp,
            datetime.fromisoformat("2021-12-09T14:19:00+00:00")
        )

        # Test invalid row length
        with self.assertRaises(ValueError):
            self.analyzer._parse_cookie_log(["cookie1"])

    def test_get_cookies_analysis(self):
        # Test for Dec 9, 2021 (two occurrences of cookie1, one of cookie2)
        target_date = date(2021, 12, 9)
        analysis = self.analyzer._get_cookies_analysis(target_date)

        self.assertEqual(analysis.max_count, 2)
        self.assertEqual(analysis.cookies_count_map["cookie1"], 2)
        self.assertEqual(analysis.cookies_count_map["cookie2"], 1)
        self.assertNotIn("cookie3", analysis.cookies_count_map)

        # Test for Dec 8, 2021 (one occurrence of cookie3)
        target_date = date(2021, 12, 8)
        analysis = self.analyzer._get_cookies_analysis(target_date)

        self.assertEqual(analysis.max_count, 1)
        self.assertEqual(analysis.cookies_count_map["cookie3"], 1)
        self.assertNotIn("cookie1", analysis.cookies_count_map)

    def test_get_most_active(self):
        # Test for Dec 9, 2021 (cookie1 is most active)
        cookies = self.analyzer.get_most_active(date(2021, 12, 9))
        self.assertEqual(cookies, ["cookie1"])

        # Test with tie for most active (modified data)
        tie_data = (
            "cookie,timestamp\n"
            "cookie1,2021-12-09T14:19:00+00:00\n"
            "cookie1,2021-12-09T14:19:00+00:00\n"
            "cookie2,2021-12-09T10:13:00+00:00\n"
            "cookie2,2021-12-09T09:13:00+00:00\n"
        )
        tie_stream = io.StringIO(tie_data)
        tie_analyzer = CookiesAnalyzer(tie_stream)
        cookies = tie_analyzer.get_most_active(date(2021, 12, 9))
        self.assertEqual(cookies, ["cookie1", "cookie2"])

        # Test with no cookies for date
        no_match = self.analyzer.get_most_active(date(2020, 1, 1))
        self.assertEqual(no_match, [])


if __name__ == "__main__":
    unittest.main()
