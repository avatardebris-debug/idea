# Phase 1 Tasks

- [x] Task 1: Project scaffolding
  - What: Create pyproject.toml, package directory structure, and __init__.py files for the csv_analyzer package
  - Files: pyproject.toml, csv_analyzer/__init__.py, csv_analyzer/cli/__init__.py, csv_analyzer/core/__init__.py, csv_analyzer/io/__init__.py
  - Done when: pyproject.toml is valid TOML with project name, version, dependencies (pandas, click), and package metadata; all __init__.py files exist; `pip install -e .` succeeds in a virtual environment

- [ ] Task 2: CSV I/O module
  - What: Build CsvReader class that reads CSV files with configurable delimiter, encoding, header handling, and type inference; build CsvWriter class that writes DataFrames back to CSV
  - Files: csv_analyzer/io/csv_reader.py, csv_analyzer/io/csv_writer.py
  - Done when: CsvReader.read() returns a pandas DataFrame with correct dtypes, handles missing files gracefully with ValueError, supports custom delimiters and encodings; CsvWriter.write() saves a DataFrame to CSV; unit tests in test_csv_io.py cover read, write, delimiter, encoding, and error cases

- [ ] Task 3: Core analysis module
  - What: Build AnalysisEngine class that performs descriptive statistics, column type detection, missing value analysis, and basic data profiling on a DataFrame
  - Files: csv_analyzer/core/analyzer.py
  - Done when: AnalysisEngine.profile() returns a dict with column types, row/column counts, missing value counts/percentages, numeric stats (mean, std, min, max, quartiles), and categorical value counts; unit tests in test_analyzer.py cover numeric columns, categorical columns, mixed types, and empty DataFrames

- [ ] Task 4: CLI entry point
  - What: Build Click-based CLI with commands: `csv-analyzer info <file>` (print profile summary), `csv-analyzer stats <file>` (print numeric column stats), `csv-analyzer head <file> [--n N]` (print first N rows as table)
  - Files: csv_analyzer/cli/main.py
  - Done when: All three CLI commands execute correctly from command line; `csv-analyzer --help` shows usage; invalid file paths produce clear error messages; unit tests in test_cli.py mock the analyzer and verify command output

- [ ] Task 5: Integration test and sample data
  - What: Create a sample CSV fixture file and an integration test that exercises the full pipeline: read CSV → analyze → output via CLI
  - Files: tests/fixtures/sample.csv, tests/test_integration.py
  - Done when: sample.csv contains 50 rows with mixed types (strings, integers, floats, dates, booleans); integration test reads the fixture, runs AnalysisEngine.profile(), and verifies the CLI output matches expected values; all tests pass with `pytest tests/`
