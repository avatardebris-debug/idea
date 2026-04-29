"""Unit tests for the report module."""

import pytest
from io import StringIO
import sys
from file_deduplicator.report import generate_report


class TestGenerateReport:
    """Tests for the generate_report function."""

    def test_generate_report_no_duplicates(self):
        """Test report generation with no duplicates."""
        duplicates = {}
        # Should not raise any exceptions
        generate_report(duplicates)

    def test_generate_report_with_duplicates(self, capsys):
        """Test report generation with duplicate files."""
        duplicates = {
            "abc123": [
                "/path/to/file1.txt",
                "/path/to/file2.txt",
            ],
        }
        generate_report(duplicates)
        captured = capsys.readouterr()
        assert "DUPLICATE FILES REPORT" in captured.out
        assert "abc123" in captured.out
        assert "file1.txt" in captured.out
        assert "file2.txt" in captured.out

    def test_generate_report_summary(self, capsys):
        """Test that the report includes a summary."""
        duplicates = {
            "abc123": ["/path/to/file1.txt", "/path/to/file2.txt"],
            "def456": ["/path/to/file3.txt", "/path/to/file4.txt"],
        }
        generate_report(duplicates)
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out
        assert "2 group(s)" in captured.out
        assert "2 duplicate file(s)" in captured.out

    def test_generate_report_marks_kept_file(self, capsys):
        """Test that the first file is marked as [KEEP]."""
        duplicates = {
            "abc123": ["/path/to/file1.txt", "/path/to/file2.txt"],
        }
        generate_report(duplicates)
        captured = capsys.readouterr()
        assert "[KEEP]" in captured.out
        assert "[DUP]" in captured.out

    def test_generate_report_empty_hash_map(self, capsys):
        """Test report with empty hash map."""
        duplicates = {}
        generate_report(duplicates)
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out
        assert "0 group(s)" in captured.out
        assert "0 duplicate file(s)" in captured.out

    def test_generate_report_multiple_files_same_hash(self, capsys):
        """Test report with multiple files sharing the same hash."""
        duplicates = {
            "abc123": [
                "/path/to/file1.txt",
                "/path/to/file2.txt",
                "/path/to/file3.txt",
                "/path/to/file4.txt",
            ],
        }
        generate_report(duplicates)
        captured = capsys.readouterr()
        assert captured.out.count("[KEEP]") == 1
        assert captured.out.count("[DUP]") == 3
