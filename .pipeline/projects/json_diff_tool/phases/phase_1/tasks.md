# Phase 1 Tasks

- [x] Task 1: Set up project structure and CLI entry point
  - What: Create the basic project structure with a Python package, main entry point, and CLI argument parsing
  - Files: Create `json_diff_tool/__init__.py`, `json_diff_tool/__main__.py`, `json_diff_tool/cli.py`
  - Done when: Running `python -m json_diff_tool --help` displays CLI options for input files and output format

- [x] Task 2: Implement JSON loading and validation
  - What: Build a function to load and validate JSON files, handling file not found and invalid JSON errors gracefully
  - Files: Create `json_diff_tool/loader.py` with `load_json(path)` function
  - Done when: `load_json()` returns parsed JSON for valid files and raises `FileNotFoundError` or `ValueError` for invalid inputs

- [x] Task 3: Implement core diff algorithm for nested objects
  - What: Create a recursive diff function that compares two JSON structures and identifies added, removed, and changed keys/values
  - Files: Create `json_diff_tool/diff.py` with `compare_json(obj1, obj2, path="")` function returning a list of diff entries
  - Done when: `compare_json()` correctly identifies: added keys, removed keys, changed values, and handles nested objects and arrays

- [x] Task 4: Implement human-readable diff output formatting
  - What: Create formatter functions to display diffs in a readable format with clear indicators for added (+), removed (-), and changed (→) entries
  - Files: Create `json_diff_tool/formatter.py` with `format_diff(diff_entries)` function
  - Done when: `format_diff()` outputs a clear, indented diff showing the path to each change with appropriate symbols

- [x] Task 5: Integrate CLI with diff functionality
  - What: Connect CLI argument parsing to the diff logic and output formatting, displaying results to stdout
  - Files: Update `json_diff_tool/cli.py` to use `loader.py`, `diff.py`, and `formatter.py`
  - Done when: Running `python -m json_diff_tool file1.json file2.json` prints a human-readable diff to stdout

- [x] Task 6: Write unit tests for core functionality
  - What: Create test suite covering edge cases: empty objects, nested structures, arrays, type mismatches, and large differences
  - Files: Create `tests/test_diff.py` with pytest tests for `compare_json()`, `load_json()`, and `format_diff()`
  - Done when: All tests pass, covering at least 8 different edge cases including nested objects and arrays