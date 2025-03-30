import sys
import argparse
from datetime import datetime, date

from .analyzer import CookiesAnalyzer


def parse_args():
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Find most active cookies for a specific day."
    )
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Cookie log file path"
    )
    parser.add_argument(
        "-d", "--date",
        required=True,
        help="Date to analyze in YYYY-MM-DD format"
    )
    return parser.parse_args()


def parse_date_input(date_input: str) -> date:
    """Parse user date inout into date object.

    Returns:
        Parsed user date input
    Raises:
        ValueError: if user date input is not correctly formatted
    """
    try:
        parsed_date = datetime.fromisoformat(date_input).date()
    except ValueError:
        raise ValueError(f"date input is not correctly formatted: '{date_input}'")
    return parsed_date


def main() -> None:
    """Main entry point for the cookie analysis program."""
    args = parse_args()

    try:
        target_date = parse_date_input(args.date)

        with open(args.file, "r") as file:
            analyzer = CookiesAnalyzer(file)
            most_active_cookies = analyzer.get_most_active(target_date)
        for cookie in most_active_cookies:
            print(cookie)
    except FileNotFoundError:
        print(f"Error: '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
