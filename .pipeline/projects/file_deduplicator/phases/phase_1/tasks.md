# Phase 1 Tasks

- [x] Task 1: Create project structure and main entry point
  - What: Set up the directory structure and create the main Python script entry point
  - Files: Create `file_deduplicator/` directory, `__init__.py`, and `main.py`
  - Done when: Project has a valid Python package structure with a main.py that can be executed via `python -m file_deduplicator`

- [x] Task 2: Implement file scanning and MD5 hashing
  - What: Build the core logic to recursively scan a directory and compute MD5 hashes for all files
  - Files: Create `file_deduplicator/scanner.py` with functions for directory traversal and hash computation
  - Done when: A function `scan_directory(path)` returns a dict mapping file paths to their MD5 hashes, tested with sample files

- [x] Task 3: Implement duplicate detection and grouping
  - What: Create logic to identify files with matching hashes and group them by hash value
  - Files: Create `file_deduplicator/duplicates.py` with function to group files by hash and identify duplicates
  - Done when: A function `find_duplicates(hash_map)` returns a dict of hash -> list of file paths for hashes with 2+ files

- [x] Task 4: Implement report generation
  - What: Build functionality to print a formatted report of duplicates grouped by hash
  - Files: Create `file_deduplicator/report.py` with function to generate and display the duplicate report
  - Done when: A function `generate_report(duplicates)` prints a clear report showing each duplicate group with file paths and hash values

- [x] Task 5: Implement CLI with --delete and --dry-run flags
  - What: Add command-line argument parsing to support scanning, reporting, optional deletion, and dry-run mode
  - Files: Update `main.py` with argparse for CLI arguments: `--path`, `--delete`, `--dry-run`
  - Done when: CLI accepts `--path` (required), `--delete` (boolean flag), and `--dry-run` (boolean flag), and executes appropriate logic based on flags

- [x] Task 6: Write unit tests
  - What: Create unit tests for scanner, duplicate detection, and report generation functions
  - Files: Create `tests/` directory with `test_scanner.py`, `test_duplicates.py`, and `test_report.py`
  - Done when: All test files exist and tests pass when run with `pytest`, covering edge cases like empty directories and single files