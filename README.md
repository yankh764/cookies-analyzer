# Cookie Analyzer

A production-grade tool that identifies the most active cookies for a specific date in cookie log files.

## Overview

This command-line utility processes cookie logs to find cookies with the highest occurrence count on a given date, following clean coding practices with maintainability and extensibility in mind.

## Usage

**Requirements**
- Python3.7+

**Example Command**
```bash
python -m cookie_analyzer.cli -f samples/cookies_log.csv -d 2023-11-20
```

**Parameters:**
- `-f, --file`: Cookie log file path (required)
- `-d, --date`: Date in YYYY-MM-DD format (required)

**Example Output:**
```
AtY0laUfhglK3lC7
```
(Multiple cookies with the same count will appear on separate lines)

## Project Structure

```
cookie_analyzer/
├── cookie_analyzer/           # Source code
│   ├── analyzer.py            # CSV parsing and analysis
│   ├── models.py              # Data structures
│   └── cli.py                 # Command-line interface
└── tests/                     # Test suite
```

## Key Design Decisions

### Modular Architecture
- Separate modules for data models, analysis logic, and CLI
- Clear separation of concerns for maintainability

### Flexible Data Parsing
- Type validation with detailed error messages
- Header-specific parsers that support future extensions

### Performance Optimization
- Early termination when past target date (uses sorted nature of logs)
- Efficient tracking of maximum cookie counts

### Robust Error Handling
- File access issues
- Date format validation
- CSV format verification

## Testing

Run tests with:
```bash
python -m unittest
```

## Assumptions

- Multiple cookies may share the highest count
- Timestamps are in UTC
- Logs are sorted by timestamp (most recent first)
- System has sufficient memory for the entire log file

---

*This project demonstrates production-grade coding practices with extensibility for future enhancements.*
*A shorter and more straightforward version could be developed, however it will sacrifice the easy extensibility for future enhancements*