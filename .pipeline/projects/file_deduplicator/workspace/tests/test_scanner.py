"""Unit tests for the scanner module."""

import os
import tempfile
import pytest
from file_deduplicator.scanner import scan_directory, compute_md5


class TestComputeMD5:
    """Tests for the compute_md5 function."""

    def test_compute_md5_single_file(self):
        """Test MD5 computation for a single file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            hash_result = compute_md5(temp_path)
            assert len(hash_result) == 32  # MD5 hash is 32 hex characters
            assert all(c in '0123456789abcdef' for c in hash_result)
        finally:
            os.unlink(temp_path)

    def test_compute_md5_empty_file(self):
        """Test MD5 computation for an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            hash_result = compute_md5(temp_path)
            assert len(hash_result) == 32
        finally:
            os.unlink(temp_path)

    def test_compute_md5_consistency(self):
        """Test that the same file produces the same hash."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for consistency")
            temp_path = f.name

        try:
            hash1 = compute_md5(temp_path)
            hash2 = compute_md5(temp_path)
            assert hash1 == hash2
        finally:
            os.unlink(temp_path)


class TestScanDirectory:
    """Tests for the scan_directory function."""

    def test_scan_directory_empty(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = scan_directory(temp_dir)
            assert result == {}

    def test_scan_directory_single_file(self):
        """Test scanning a directory with a single file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("Test content")

            result = scan_directory(temp_dir)
            assert len(result) == 1
            assert test_file in result

    def test_scan_directory_multiple_files(self):
        """Test scanning a directory with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(5):
                test_file = os.path.join(temp_dir, f"file{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"Content {i}")

            result = scan_directory(temp_dir)
            assert len(result) == 5

    def test_scan_directory_recursive(self):
        """Test scanning a directory recursively."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create subdirectory with files
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)
            
            for i in range(3):
                test_file = os.path.join(subdir, f"file{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"Content {i}")

            result = scan_directory(temp_dir)
            assert len(result) == 3

    def test_scan_directory_no_duplicates_in_result(self):
        """Test that each file appears only once in the result."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("Test content")

            result = scan_directory(temp_dir)
            assert len(result) == 1
            assert test_file in result

    def test_scan_directory_returns_absolute_paths(self):
        """Test that scan_directory returns absolute paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("Test content")

            result = scan_directory(temp_dir)
            for path in result.keys():
                assert os.path.isabs(path)
