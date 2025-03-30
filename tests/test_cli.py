import io
import unittest
import tempfile
from datetime import date
from unittest.mock import patch

from cookie_analyzer.cli import parse_args, parse_date_input, main


class TestCLI(unittest.TestCase):
    def setUp(self):
        # Create a temporary cookie log file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.temp_file.write(
            "cookie,timestamp\n"
            "cookie1,2021-12-09T14:19:00+00:00\n"
            "cookie2,2021-12-09T10:13:00+00:00\n"
            "cookie1,2021-12-09T07:25:00+00:00\n"
            "cookie3,2021-12-08T22:03:00+00:00\n"
        )
        self.temp_file.close()

    def tearDown(self):
        import os
        os.unlink(self.temp_file.name)

    def test_parse_date_input(self):
        # Test valid date format
        self.assertEqual(parse_date_input("2021-12-09"), date(2021, 12, 9))

        # Test invalid date format
        with self.assertRaises(ValueError):
            parse_date_input("12-09-2021")

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_args(self, mock_parse_args):
        # Setup mock arguments
        mock_parse_args.return_value = unittest.mock.Mock(
            file="test.csv", date="2021-12-09"
        )

        # Test argument parsing
        args = parse_args()
        self.assertEqual(args.file, "test.csv")
        self.assertEqual(args.date, "2021-12-09")

    @patch("sys.argv", ["command", "-f", "file.csv", "-d", "2021-12-09"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_success(self, mock_stdout):
        # Patch sys.argv and execute main with our temp file
        with patch("sys.argv", ["command", "-f", self.temp_file.name, "-d", "2021-12-09"]):
            main()
            self.assertEqual(mock_stdout.getvalue().strip(), "cookie1")

    @patch("sys.argv", ["command", "-f", "nonexistent.csv", "-d", "2021-12-09"])
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.exit")
    def test_main_file_not_found(self, mock_exit, mock_stderr):
        main()
        self.assertIn("not found", mock_stderr.getvalue())
        mock_exit.assert_called_with(1)

    @patch("sys.argv", ["command", "-f", "file.csv", "-d", "invalid-date"])
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.exit")
    def test_main_invalid_date(self, mock_exit, mock_stderr):
        main()
        self.assertIn("not correctly formatted", mock_stderr.getvalue())
        mock_exit.assert_called_with(1)


if __name__ == "__main__":
    unittest.main()
