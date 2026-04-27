"""Tests for csv_analyzer.cli — CLI commands."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_analyzer.cli.main import cli


class TestCliInfo:
    """Tests for the 'info' CLI command."""

    def test_info_basic(self, tmp_path: Path) -> None:
        """Test the info command with a basic CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        assert result.exit_code == 0
        assert "Rows: 2" in result.output
        assert "Columns: 3" in result.output
        assert "name" in result.output
        assert "age" in result.output

    def test_info_no_numeric_columns(self, tmp_path: Path) -> None:
        """Test the info command with no numeric columns."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,city\nAlice,NYC\nBob,LA\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        assert result.exit_code == 0
        assert "Numeric Statistics:" not in result.output

    def test_info_file_not_found(self) -> None:
        """Test the info command with a non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "/nonexistent/file.csv"])

        assert result.exit_code != 0
        assert "Error" in result.output

    def test_info_empty_file(self, tmp_path: Path) -> None:
        """Test the info command with an empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        # Should handle gracefully, even if exit code is non-zero
        assert "Error" in result.output or "Rows: 0" in result.output


class TestCliStats:
    """Tests for the 'stats' CLI command."""

    def test_stats_basic(self, tmp_path: Path) -> None:
        """Test the stats command with numeric columns."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,score\nAlice,30,95.5\nBob,25,88.0\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(csv_file)])

        assert result.exit_code == 0
        assert "age" in result.output.lower()
        assert "score" in result.output.lower()
        assert "mean" in result.output.lower()
        assert "std" in result.output.lower()

    def test_stats_no_numeric_columns(self, tmp_path: Path) -> None:
        """Test the stats command with no numeric columns."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,city\nAlice,NYC\nBob,LA\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(csv_file)])

        assert result.exit_code == 0
        assert "numeric" in result.output.lower()

    def test_stats_file_not_found(self) -> None:
        """Test the stats command with a non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", "/nonexistent/file.csv"])

        assert result.exit_code != 0
        assert "Error" in result.output


class TestCliHead:
    """Tests for the 'head' CLI command."""

    def test_head_basic(self, tmp_path: Path) -> None:
        """Test the head command with a CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Boston\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["head", str(csv_file), "--n", "2"])

        assert result.exit_code == 0
        assert "Alice" in result.output
        assert "Bob" in result.output
        assert "Charlie" not in result.output

    def test_head_file_not_found(self) -> None:
        """Test the head command with a non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["head", "/nonexistent/file.csv"])

        assert result.exit_code != 0
        assert "Error" in result.output


class TestCliIntegration:
    """Integration tests for CLI commands."""

    def test_cli_info_with_real_data(self, tmp_path: Path) -> None:
        """Test CLI info command with realistic data."""
        csv_file = tmp_path / "employees.csv"
        csv_file.write_text(
            "name,age,department,salary\n"
            "Alice,30,Engineering,75000\n"
            "Bob,25,Marketing,65000\n"
            "Charlie,35,Engineering,85000\n"
            "Diana,28,HR,70000\n"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        assert result.exit_code == 0
        assert "Rows: 4" in result.output
        assert "Columns: 4" in result.output
        assert "Engineering" in result.output
        assert "mean" in result.output.lower()

    def test_cli_stats_with_real_data(self, tmp_path: Path) -> None:
        """Test CLI stats command with realistic data."""
        csv_file = tmp_path / "sales.csv"
        csv_file.write_text(
            "product,units_sold,revenue\n"
            "Widget A,100,5000\n"
            "Widget B,150,7500\n"
            "Widget C,75,3750\n"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(csv_file)])

        assert result.exit_code == 0
        assert "units_sold" in result.output
        assert "revenue" in result.output
        assert "mean" in result.output
        assert "std" in result.output

    def test_cli_head_with_real_data(self, tmp_path: Path) -> None:
        """Test CLI head command with realistic data."""
        csv_file = tmp_path / "products.csv"
        csv_file.write_text(
            "id,name,price,category\n"
            "1,Widget,19.99,Electronics\n"
            "2,Gadget,29.99,Electronics\n"
            "3,Tool,9.99,Hardware\n"
            "4,Device,49.99,Electronics\n"
            "5,Instrument,39.99,Hardware\n"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["head", str(csv_file), "--n", "3"])

        assert result.exit_code == 0
        assert "Widget" in result.output
        assert "Gadget" in result.output
        assert "Tool" in result.output
        assert "Device" not in result.output
        assert "Instrument" not in result.output


class TestCliEdgeCases:
    """CLI tests for edge cases."""

    def test_large_file_handling(self, tmp_path: Path) -> None:
        """Test handling of larger files."""
        csv_file = tmp_path / "large.csv"
        with open(csv_file, "w", newline="") as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(["id", "value", "category"])
            for i in range(1000):
                writer.writerow([i, i * 10, f"cat_{i % 10}"])

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        assert result.exit_code == 0
        assert "Rows: 1000" in result.output
        assert "Columns: 3" in result.output

    def test_unicode_content(self, tmp_path: Path) -> None:
        """Test handling of Unicode content."""
        csv_file = tmp_path / "unicode.csv"
        csv_file.write_text(
            "name,city,country\n"
            "José García,México,México\n"
            "María López,España,España\n"
            "李明，北京，中国\n"
            "田中太郎，東京，日本\n"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["head", str(csv_file)])

        assert result.exit_code == 0
        assert "José" in result.output
        assert "María" in result.output
        assert "李明" in result.output
        assert "田中太郎" in result.output

    def test_mixed_numeric_types(self, tmp_path: Path) -> None:
        """Test handling of mixed numeric types (int and float)."""
        csv_file = tmp_path / "mixed.csv"
        csv_file.write_text(
            "id,price,quantity\n"
            "1,19.99,100\n"
            "2,29.99,150\n"
            "3,9.99,75\n"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(csv_file)])

        assert result.exit_code == 0
        assert "price" in result.output
        assert "quantity" in result.output

    def test_empty_dataframe(self, tmp_path: Path) -> None:
        """Test handling of empty DataFrames."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("name,age,city\n")  # Header only

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        assert result.exit_code == 0 or "Error" in result.output
        assert "Columns: 3" in result.output

    def test_single_column(self, tmp_path: Path) -> None:
        """Test handling of single-column DataFrames."""
        csv_file = tmp_path / "single.csv"
        csv_file.write_text("value\n1\n2\n3\n4\n5\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(csv_file)])

        assert result.exit_code == 0
        assert "value" in result.output
        assert "mean" in result.output


class TestCliErrorHandling:
    """CLI tests for error handling."""

    def test_invalid_csv_format(self, tmp_path: Path) -> None:
        """Test handling of malformed CSV files."""
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25\n")  # Missing column

        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(csv_file)])

        # Should handle gracefully
        assert result.exit_code == 0 or "Error" in result.output

    def test_permission_denied(self, tmp_path: Path) -> None:
        """Test handling of permission errors."""
        csv_file = tmp_path / "readonly.csv"
        csv_file.write_text("name,age\nAlice,30\n")
        csv_file.chmod(0o000)

        try:
            runner = CliRunner()
            result = runner.invoke(cli, ["info", str(csv_file)])
            # If we get here, the file was readable (e.g., running as root)
            assert result.exit_code == 0 or "Error" in result.output
        except PermissionError:
            # Expected if running as non-root user
            pass
        finally:
            csv_file.chmod(0o644)  # Restore permissions
