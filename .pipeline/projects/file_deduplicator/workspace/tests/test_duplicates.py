"""Unit tests for the duplicates module."""

import pytest
from file_deduplicator.duplicates import find_duplicates


class TestFindDuplicates:
    """Tests for the find_duplicates function."""

    def test_find_duplicates_no_duplicates(self):
        """Test when there are no duplicate files."""
        hash_map = {
            "/path/to/file1.txt": "abc123",
            "/path/to/file2.txt": "def456",
            "/path/to/file3.txt": "ghi789",
        }
        result = find_duplicates(hash_map)
        assert result == {}

    def test_find_duplicates_with_duplicates(self):
        """Test when there are duplicate files."""
        hash_map = {
            "/path/to/file1.txt": "abc123",
            "/path/to/file2.txt": "abc123",  # Duplicate of file1
            "/path/to/file3.txt": "def456",
            "/path/to/file4.txt": "abc123",  # Another duplicate
        }
        result = find_duplicates(hash_map)
        assert "abc123" in result
        assert len(result["abc123"]) == 3
        assert "def456" not in result

    def test_find_duplicates_empty_input(self):
        """Test with empty hash map."""
        result = find_duplicates({})
        assert result == {}

    def test_find_duplicates_single_file(self):
        """Test with a single file (no duplicates possible)."""
        hash_map = {
            "/path/to/file1.txt": "abc123",
        }
        result = find_duplicates(hash_map)
        assert result == {}

    def test_find_duplicates_all_duplicates(self):
        """Test when all files are duplicates of each other."""
        hash_map = {
            "/path/to/file1.txt": "abc123",
            "/path/to/file2.txt": "abc123",
            "/path/to/file3.txt": "abc123",
        }
        result = find_duplicates(hash_map)
        assert len(result) == 1
        assert "abc123" in result
        assert len(result["abc123"]) == 3

    def test_find_duplicates_preserves_all_duplicate_files(self):
        """Test that all duplicate files are preserved in the result."""
        hash_map = {
            "/path/to/file1.txt": "abc123",
            "/path/to/file2.txt": "abc123",
            "/path/to/file3.txt": "abc123",
            "/path/to/file4.txt": "def456",
            "/path/to/file5.txt": "def456",
        }
        result = find_duplicates(hash_map)
        assert len(result["abc123"]) == 3
        assert len(result["def456"]) == 2

    def test_find_duplicates_returns_lists(self):
        """Test that the function returns lists of file paths."""
        hash_map = {
            "/path/to/file1.txt": "abc123",
            "/path/to/file2.txt": "abc123",
        }
        result = find_duplicates(hash_map)
        for files in result.values():
            assert isinstance(files, list)
            assert all(isinstance(f, str) for f in files)
