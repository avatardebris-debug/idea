# Master Ideas List

Ideas are processed top-to-bottom. The pipeline picks the first unchecked `[ ]` item.

## Format
`- [ ] **Title** — Description of what to build`

## Ideas

- [ ] **CSV Analyzer** — Build a Python CLI tool that reads a CSV file and prints summary statistics (row count, column names, min/max/mean for numeric columns, null counts). Include argparse, error handling for missing files and malformed CSVs, and unit tests with sample fixture files.

- [ ] **File Deduplicator** — Build a Python script that scans a directory recursively, finds duplicate files by MD5 hash, and prints a report of duplicates grouped by hash. Optionally deletes duplicates with a --delete flag (with dry-run mode). Include unit tests.

- [ ] **Markdown to HTML Converter** — Build a Python CLI that converts a markdown file to a standalone HTML file with basic CSS styling. Support headers, bold, italic, code blocks, and links. Include unit tests for each element type.

- [ ] **URL Health Checker** — Build a Python CLI that reads a list of URLs from a text file, sends HEAD requests (with timeout), and outputs a report showing status code, response time, and whether each URL is up or down. Include concurrent checking with threading and unit tests with mock HTTP responses.

- [ ] **JSON Diff Tool** — Build a Python CLI that compares two JSON files and prints a human-readable diff showing added, removed, and changed keys/values. Handle nested objects and arrays. Include unit tests covering edge cases.
