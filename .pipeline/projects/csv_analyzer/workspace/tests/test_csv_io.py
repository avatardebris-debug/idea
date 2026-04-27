"""Tests for csv_analyzer.io — CsvReader and CsvWriter."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest
import pandas as pd

from csv_analyzer.io.csv_reader import CsvReader
from csv_analyzer.io.csv_writer import CsvWriter


# ── CsvReader Tests ──────────────────────────────────────────────────────────


class TestCsvReader:
    """Tests for the CsvReader class."""

    def test_read_basic_csv(self, tmp_path: Path) -> None:
        """Test reading a basic CSV file."""
        csv_file = tmp_path / "basic.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        reader = CsvReader()
        df = reader.read(csv_file)

        assert len(df) == 2
        assert list(df.columns) == ["name", "age", "city"]
        assert df["name"].iloc[0] == "Alice"
        assert df["age"].iloc[0] == 30

    def test_read_custom_delimiter(self, tmp_path: Path) -> None:
        """Test reading a CSV with a custom delimiter."""
        csv_file = tmp_path / "tsv.csv"
        csv_file.write_text("name\tage\tcity\nAlice\t30\tNYC\nBob\t25\tLA\n")

        reader = CsvReader(delimiter="\t")
        df = reader.read(csv_file)

        assert len(df) == 2
        assert list(df.columns) == ["name", "age", "city"]

    def test_read_custom_encoding(self, tmp_path: Path) -> None:
        """Test reading a CSV with a specific encoding."""
        csv_file = tmp_path / "latin1.csv"
        csv_file.write_text("name\nJosé\nMaría\n", encoding="latin-1")

        reader = CsvReader(encoding="latin-1")
        df = reader.read(csv_file)

        assert df["name"].iloc[0] == "José"
        assert df["name"].iloc[1] == "María"

    def test_read_missing_file_raises(self) -> None:
        """Test that reading a non-existent file raises FileNotFoundError."""
        reader = CsvReader()
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            reader.read("/nonexistent/path/file.csv")

    def test_read_non_file_raises(self, tmp_path: Path) -> None:
        """Test that reading a directory raises ValueError."""
        dir_path = tmp_path / "a_directory"
        dir_path.mkdir()

        reader = CsvReader()
        with pytest.raises(ValueError, match="Path is not a file"):
            reader.read(dir_path)

    def test_read_empty_file_raises(self, tmp_path: Path) -> None:
        """Test that reading an empty file raises EmptyDataError."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        reader = CsvReader()
        with pytest.raises(pd.errors.EmptyDataError):
            reader.read(csv_file)

    def test_read_with_header_none(self, tmp_path: Path) -> None:
        """Test reading a CSV with no header row."""
        csv_file = tmp_path / "no_header.csv"
        csv_file.write_text("Alice,30,NYC\nBob,25,LA\n")

        reader = CsvReader(header=None, names=[0, 1, 2])
        df = reader.read(csv_file)

        # Without header, pandas assigns integer column names
        assert list(df.columns) == [0, 1, 2]
        assert len(df) == 2

    def test_read_with_usecols(self, tmp_path: Path) -> None:
        """Test reading only specific columns."""
        csv_file = tmp_path / "cols.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        reader = CsvReader(usecols=["name", "city"])
        df = reader.read(csv_file)

        assert list(df.columns) == ["name", "city"]
        assert len(df) == 2

    def test_read_with_na_values(self, tmp_path: Path) -> None:
        """Test reading with custom NA values."""
        csv_file = tmp_path / "na.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,N/A\n")

        reader = CsvReader(na_values=["N/A"])
        df = reader.read(csv_file)

        assert pd.isna(df["age"].iloc[1])

    def test_read_with_dtype(self, tmp_path: Path) -> None:
        """Test reading with explicit dtypes."""
        csv_file = tmp_path / "dtype.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,25\n")

        reader = CsvReader(dtype={"age": "int64"})
        df = reader.read(csv_file)

        assert df["age"].dtype in (int, "int64", pd.Int64Dtype())
        assert df["age"].iloc[0] == 30

    def test_read_with_string_path(self, tmp_path: Path) -> None:
        """Test that CsvReader accepts string paths."""
        csv_file = tmp_path / "str_path.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        reader = CsvReader()
        df = reader.read(str(csv_file))

        assert len(df) == 1

    def test_read_with_pathlib_path(self, tmp_path: Path) -> None:
        """Test that CsvReader accepts Path objects."""
        csv_file = tmp_path / "pathlib.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        reader = CsvReader()
        df = reader.read(csv_file)

        assert len(df) == 1


class TestCsvReaderClassMethod:
    """Tests for CsvReader.read_with_type_inference class method."""

    def test_type_inference(self, tmp_path: Path) -> None:
        """Test that type inference works correctly."""
        csv_file = tmp_path / "infer.csv"
        csv_file.write_text("name,age,score,active\nAlice,30,95.5,true\nBob,25,88.0,false\n")

        df = CsvReader.read_with_type_inference(csv_file)

        assert df["age"].dtype in (int, "int64", pd.Int64Dtype())
        assert df["score"].dtype in (float, "float64")
        assert len(df) == 2


# ── CsvWriter Tests ──────────────────────────────────────────────────────────


class TestCsvWriter:
    """Tests for the CsvWriter class."""

    def test_write_basic(self, tmp_path: Path) -> None:
        """Test writing a basic DataFrame to CSV."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        writer = CsvWriter(index=False)
        output = tmp_path / "output.csv"

        result_path = writer.write(df, output)

        assert result_path == output
        assert output.exists()

        # Verify content
        read_df = pd.read_csv(output)
        assert len(read_df) == 2
        assert list(read_df.columns) == ["name", "age"]

    def test_write_custom_delimiter(self, tmp_path: Path) -> None:
        """Test writing with a custom delimiter."""
        df = pd.DataFrame({"name": ["Alice"], "age": [30]})
        writer = CsvWriter(delimiter="\t")
        output = tmp_path / "output.tsv"

        writer.write(df, output)

        content = output.read_text()
        assert "\t" in content

    def test_write_no_index(self, tmp_path: Path) -> None:
        """Test writing without row indices."""
        df = pd.DataFrame({"name": ["Alice"], "age": [30]})
        writer = CsvWriter(index=False)
        output = tmp_path / "no_index.csv"

        writer.write(df, output)

        content = output.read_text()
        # Should not have an index column (no leading number)
        lines = content.strip().split("\n")
        assert len(lines) == 2  # header + 1 data row
        assert "," in lines[0]  # header has commas

    def test_write_overwrite_false_raises(self, tmp_path: Path) -> None:
        """Test that writing to an existing file raises FileExistsError."""
        existing = tmp_path / "existing.csv"
        existing.write_text("a,b\n1,2\n")

        df = pd.DataFrame({"x": [1]})
        writer = CsvWriter()

        with pytest.raises(FileExistsError, match="File already exists"):
            writer.write(df, existing)

    def test_write_overwrite_true(self, tmp_path: Path) -> None:
        """Test that overwrite=True allows overwriting."""
        existing = tmp_path / "overwrite.csv"
        existing.write_text("old,data\n1,2\n")

        df = pd.DataFrame({"new": [3]})
        writer = CsvWriter()

        result_path = writer.write(df, existing, overwrite=True)

        assert result_path == existing
        content = existing.read_text()
        assert "new" in content
        assert "old" not in content

    def test_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Test that writer creates parent directories if they don't exist."""
        df = pd.DataFrame({"a": [1]})
        writer = CsvWriter()
        output = tmp_path / "deep" / "nested" / "dir" / "file.csv"

        result_path = writer.write(df, output)

        assert result_path == output
        assert output.exists()

    def test_write_na_rep(self, tmp_path: Path) -> None:
        """Test writing with custom NA representation."""
        df = pd.DataFrame({"name": ["Alice"], "age": [None]})
        writer = CsvWriter(na_rep="MISSING")
        output = tmp_path / "na.csv"

        writer.write(df, output)

        content = output.read_text()
        assert "MISSING" in content

    def test_write_roundtrip(self, tmp_path: Path) -> None:
        """Test that writing and reading back produces the same data."""
        original = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [30, 25],
            "city": ["NYC", "LA"],
        })

        writer = CsvWriter(index=False)
        output = tmp_path / "roundtrip.csv"
        writer.write(original, output)

        read_df = pd.read_csv(output)
        pd.testing.assert_frame_equal(original, read_df)
