"""CsvReader — reads CSV files into pandas DataFrames with configurable options."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


class CsvReader:
    """Read CSV files with configurable delimiter, encoding, and header handling.

    Parameters
    ----------
    delimiter : str, optional
        Character used to separate fields. Defaults to ','.
    encoding : str, optional
        File encoding. Defaults to 'utf-8'.
    header : int | list[int] | None, optional
        Row number(s) to use as column names. None means no header.
    dtype : dict[str, type] | type, optional
        Data types for columns or all columns.
    usecols : list[str] | None, optional
        Columns to read.
    na_values : list[str] | None, optional
        Additional strings to recognize as NA/NaN.
    """

    def __init__(
        self,
        delimiter: str = ",",
        encoding: str = "utf-8",
        header: int | list[int] | None = 0,
        dtype: dict[str, type] | type | None = None,
        usecols: list[str] | None = None,
        na_values: list[str] | None = None,
    ) -> None:
        self.delimiter = delimiter
        self.encoding = encoding
        self.header = header
        self.dtype = dtype
        self.usecols = usecols
        self.na_values = na_values

    def read(self, filepath: str | Path) -> pd.DataFrame:
        """Read a CSV file and return a DataFrame.

        Parameters
        ----------
        filepath : str or Path
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            The parsed DataFrame.

        Raises
        ------
        ValueError
            If the file does not exist or is not a file.
        FileNotFoundError
            If the file cannot be found.
        pd.errors.EmptyDataError
            If the file is empty.
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {filepath}")

        if path.stat().st_size == 0:
            raise pd.errors.EmptyDataError("The CSV file is empty")

        kwargs: dict = {
            "sep": self.delimiter,
            "encoding": self.encoding,
            "header": self.header,
            "dtype": self.dtype,
            "usecols": self.usecols,
            "na_values": self.na_values,
        }

        # Remove None values so pandas uses its defaults
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        return pd.read_csv(path, **kwargs)

    @classmethod
    def read_with_type_inference(
        cls,
        filepath: str | Path,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> pd.DataFrame:
        """Read a CSV file letting pandas infer types automatically.

        This is a convenience method that uses the default CsvReader settings
        which enable pandas' automatic type inference.

        Parameters
        ----------
        filepath : str or Path
            Path to the CSV file.
        delimiter : str, optional
            Field separator. Defaults to ','.
        encoding : str, optional
            File encoding. Defaults to 'utf-8'.

        Returns
        -------
        pd.DataFrame
            The parsed DataFrame with inferred types.
        """
        reader = cls(delimiter=delimiter, encoding=encoding)
        return reader.read(filepath)
