"""Tests for csv_analyzer.core — AnalysisEngine."""

from __future__ import annotations

import pandas as pd
import pytest

from csv_analyzer.core.analyzer import AnalysisEngine


class TestAnalysisEngine:
    """Tests for the AnalysisEngine class."""

    def test_profile_basic(self) -> None:
        """Test basic profiling of a simple DataFrame."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            "score": [95.5, 88.0, 92.0],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert profile["row_count"] == 3
        assert profile["column_count"] == 3
        assert "name" in profile["column_types"]
        assert "age" in profile["numeric_stats"]
        assert "score" in profile["numeric_stats"]

    def test_profile_numeric_columns(self) -> None:
        """Test profiling with numeric columns."""
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [10.5, 20.3, 15.7, 18.2, 22.1],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "a" in profile["numeric_stats"]
        assert "b" in profile["numeric_stats"]
        assert profile["numeric_stats"]["a"]["count"] == 5
        assert profile["numeric_stats"]["a"]["mean"] == 3.0
        assert profile["numeric_stats"]["a"]["median"] == 3.0
        assert profile["numeric_stats"]["a"]["min"] == 1.0
        assert profile["numeric_stats"]["a"]["max"] == 5.0

    def test_profile_categorical_columns(self) -> None:
        """Test profiling with categorical columns."""
        df = pd.DataFrame({
            "category": ["A", "B", "A", "C", "B", "A"],
            "value": [1, 2, 3, 4, 5, 6],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "category" in profile["categorical_stats"]
        assert profile["categorical_stats"]["category"]["unique_count"] == 3
        assert profile["categorical_stats"]["category"]["value_counts"]["A"] == 3

    def test_profile_missing_values(self) -> None:
        """Test profiling with missing values."""
        df = pd.DataFrame({
            "a": [1, 2, None, 4, 5],
            "b": [10, 20, 30, 40, 50],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "a" in profile["missing_values"]
        assert profile["missing_values"]["a"]["count"] == 1
        assert profile["missing_values"]["a"]["percentage"] == 20.0
        assert profile["missing_values"]["b"]["count"] == 0

    def test_get_numeric_columns(self) -> None:
        """Test getting numeric column names."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [30, 25],
            "score": [95.5, 88.0],
        })
        engine = AnalysisEngine(df)

        numeric_cols = engine.get_numeric_columns()
        assert set(numeric_cols) == {"age", "score"}

    def test_get_categorical_columns(self) -> None:
        """Test getting categorical column names."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [30, 25],
            "city": ["NYC", "LA"],
        })
        engine = AnalysisEngine(df)

        categorical_cols = engine.get_categorical_columns()
        assert set(categorical_cols) == {"name", "city"}

    def test_get_summary_stats(self) -> None:
        """Test getting summary statistics DataFrame."""
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [10.0, 20.0, 30.0, 40.0, 50.0],
            "c": ["x", "y", "z", "w", "v"],
        })
        engine = AnalysisEngine(df)
        summary = engine.get_summary_stats()

        assert "a" in summary.index
        assert "b" in summary.index
        assert "c" not in summary.index
        assert summary.loc["a", "mean"] == 3.0
        assert summary.loc["b", "mean"] == 30.0

    def test_profile_empty_dataframe(self) -> None:
        """Test profiling an empty DataFrame."""
        df = pd.DataFrame()
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert profile["row_count"] == 0
        assert profile["column_count"] == 0
        assert profile["numeric_stats"] == {}
        assert profile["categorical_stats"] == {}

    def test_profile_single_row(self) -> None:
        """Test profiling a DataFrame with a single row."""
        df = pd.DataFrame({
            "a": [1],
            "b": [2.5],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert profile["row_count"] == 1
        assert profile["numeric_stats"]["a"]["count"] == 1
        assert profile["numeric_stats"]["a"]["mean"] == 1.0
        assert profile["numeric_stats"]["a"]["std"] is None  # std of single value is undefined

    def test_profile_all_missing_numeric(self) -> None:
        """Test profiling numeric column with all missing values."""
        df = pd.DataFrame({
            "a": [None, None, None],
            "b": [1, 2, 3],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "a" in profile["numeric_stats"]
        assert profile["numeric_stats"]["a"]["count"] == 0
        assert profile["numeric_stats"]["a"]["mean"] is None

    def test_profile_mixed_types(self) -> None:
        """Test profiling DataFrame with mixed column types."""
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "int_col" in profile["numeric_stats"]
        assert "float_col" in profile["numeric_stats"]
        assert "str_col" in profile["categorical_stats"]
        # bool_col is treated as numeric in pandas
        assert "bool_col" in profile["numeric_stats"]

    def test_profile_with_nan_in_numeric(self) -> None:
        """Test profiling numeric column with NaN values."""
        df = pd.DataFrame({
            "a": [1.0, 2.0, None, 4.0, 5.0],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert profile["numeric_stats"]["a"]["count"] == 4
        assert profile["numeric_stats"]["a"]["mean"] == 3.0
        assert profile["missing_values"]["a"]["count"] == 1

class TestAnalysisEngineEdgeCases:
    """Additional edge case tests for AnalysisEngine."""

    def test_profile_with_all_nan_numeric(self) -> None:
        """Test profiling numeric column with all NaN values."""
        df = pd.DataFrame({
            "a": [None, None, None],
            "b": [1, 2, 3],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "a" in profile["numeric_stats"]
        assert profile["numeric_stats"]["a"]["count"] == 0
        assert profile["numeric_stats"]["a"]["mean"] is None
        assert profile["numeric_stats"]["a"]["std"] is None
        assert profile["numeric_stats"]["a"]["min"] is None
        assert profile["numeric_stats"]["a"]["max"] is None
        assert profile["numeric_stats"]["a"]["median"] is None

    def test_profile_with_special_floats(self) -> None:
        """Test profiling with special float values (inf, -inf, nan)."""
        df = pd.DataFrame({
            "a": [1.0, float('inf'), float('-inf'), float('nan')],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "a" in profile["numeric_stats"]
        assert profile["numeric_stats"]["a"]["count"] == 3  # inf, -inf, nan excluded
        assert profile["missing_values"]["a"]["count"] == 1  # nan counted as missing

    def test_get_summary_stats_empty(self) -> None:
        """Test get_summary_stats with no numeric columns."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "city": ["NYC", "LA"],
        })
        engine = AnalysisEngine(df)
        summary = engine.get_summary_stats()

        assert summary.empty

    def test_profile_with_boolean_column(self) -> None:
        """Test profiling boolean columns."""
        df = pd.DataFrame({
            "flag": [True, False, True, False, True],
            "value": [1, 2, 3, 4, 5],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        # Boolean columns are treated as numeric in pandas
        assert "flag" in profile["numeric_stats"]
        assert profile["numeric_stats"]["flag"]["mean"] == 0.6

    def test_profile_with_datetime_column(self) -> None:
        """Test profiling datetime columns."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
            "value": [1, 2, 3],
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        # Datetime columns are treated as categorical
        assert "date" in profile["categorical_stats"]
        assert profile["categorical_stats"]["date"]["unique_count"] == 3

    def test_profile_with_mixed_numeric_precision(self) -> None:
        """Test profiling with mixed int and float columns."""
        df = pd.DataFrame({
            "int_col": pd.array([1, 2, 3], dtype="Int64"),
            "float_col": pd.array([1.0, 2.0, 3.0], dtype="float64"),
        })
        engine = AnalysisEngine(df)
        profile = engine.profile()

        assert "int_col" in profile["numeric_stats"]
        assert "float_col" in profile["numeric_stats"]
        assert profile["numeric_stats"]["int_col"]["mean"] == 2.0
        assert profile["numeric_stats"]["float_col"]["mean"] == 2.0
