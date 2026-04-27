"""AnalysisEngine — performs descriptive statistics and data profiling on DataFrames."""

from __future__ import annotations

from typing import Any

import pandas as pd


class AnalysisEngine:
    """Analyze pandas DataFrames with descriptive statistics and profiling.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to analyze.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """Initialize the AnalysisEngine with a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to analyze.
        """
        self.df = df

    def profile(self) -> dict[str, Any]:
        """Generate a comprehensive profile of the DataFrame.

        Returns
        -------
        dict
            A dictionary containing:
            - column_types: dict mapping column names to their inferred types
            - numeric_stats: dict of statistics for numeric columns
            - categorical_stats: dict of statistics for categorical columns
            - missing_values: dict of missing value counts and percentages
            - row_count: total number of rows
            - column_count: total number of columns
        """
        profile = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "column_types": {},
            "numeric_stats": {},
            "categorical_stats": {},
            "missing_values": {},
        }

        for col in self.df.columns:
            # Column type
            profile["column_types"][col] = self._infer_column_type(col)

            # Missing values
            missing_count = self.df[col].isna().sum()
            missing_pct = (missing_count / len(self.df)) * 100 if len(self.df) > 0 else 0.0
            profile["missing_values"][col] = {
                "count": int(missing_count),
                "percentage": round(missing_pct, 2),
            }

            # Numeric statistics
            if self._is_numeric_column(col):
                profile["numeric_stats"][col] = self._get_numeric_stats(col)

            # Categorical statistics
            if self._is_categorical_column(col):
                profile["categorical_stats"][col] = self._get_categorical_stats(col)

        return profile

    def get_numeric_columns(self) -> list[str]:
        """Get names of numeric columns.

        Returns
        -------
        list[str]
            List of column names that are numeric.
        """
        return [col for col in self.df.columns if self._is_numeric_column(col)]

    def get_categorical_columns(self) -> list[str]:
        """Get names of categorical columns.

        Returns
        -------
        list[str]
            List of column names that are categorical.
        """
        return [col for col in self.df.columns if self._is_categorical_column(col)]

    def get_summary_stats(self) -> pd.DataFrame:
        """Get summary statistics for numeric columns.

        Returns
        -------
        pd.DataFrame
            DataFrame with summary statistics for numeric columns.
        """
        numeric_cols = self.get_numeric_columns()
        if not numeric_cols:
            return pd.DataFrame()

        summary = pd.DataFrame(index=numeric_cols)
        summary["count"] = self.df[numeric_cols].count()
        summary["mean"] = self.df[numeric_cols].mean()
        summary["std"] = self.df[numeric_cols].std()
        summary["min"] = self.df[numeric_cols].min()
        summary["max"] = self.df[numeric_cols].max()
        summary["median"] = self.df[numeric_cols].median()

        return summary

    def _infer_column_type(self, col: str) -> str:
        """Infer the type of a column.

        Parameters
        ----------
        col : str
            Column name.

        Returns
        -------
        str
            Column type as a string.
        """
        if self._is_numeric_column(col):
            return "numeric"
        elif self._is_categorical_column(col):
            return "categorical"
        else:
            return "unknown"

    def _is_numeric_column(self, col: str) -> bool:
        """Check if a column is numeric.

        Parameters
        ----------
        col : str
            Column name.

        Returns
        -------
        bool
            True if the column is numeric.
        """
        return pd.api.types.is_numeric_dtype(self.df[col])

    def _is_categorical_column(self, col: str) -> bool:
        """Check if a column is categorical.

        Parameters
        ----------
        col : str
            Column name.

        Returns
        -------
        bool
            True if the column is categorical.
        """
        return pd.api.types.is_string_dtype(self.df[col]) or pd.api.types.is_bool_dtype(self.df[col])

    def _get_numeric_stats(self, col: str) -> dict[str, Any]:
        """Get statistics for a numeric column.

        Parameters
        ----------
        col : str
            Column name.

        Returns
        -------
        dict
            Dictionary of statistics.
        """
        series = self.df[col].dropna()
        count = len(series)

        if count == 0:
            return {
                "count": 0,
                "mean": None,
                "std": None,
                "min": None,
                "max": None,
                "median": None,
            }

        return {
            "count": int(count),
            "mean": float(series.mean()) if count > 0 else None,
            "std": float(series.std()) if count > 1 else None,
            "min": float(series.min()) if count > 0 else None,
            "max": float(series.max()) if count > 0 else None,
            "median": float(series.median()) if count > 0 else None,
        }

    def _get_categorical_stats(self, col: str) -> dict[str, Any]:
        """Get statistics for a categorical column.

        Parameters
        ----------
        col : str
            Column name.

        Returns
        -------
        dict
            Dictionary of statistics.
        """
        series = self.df[col].dropna()
        value_counts = series.value_counts().to_dict()

        return {
            "unique_count": int(series.nunique()),
            "value_counts": value_counts,
        }
