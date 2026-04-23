"""CsvWriter — writes pandas DataFrames to CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class CsvWriter:
    """Write pandas DataFrames to CSV files.

    Parameters
    ----------
    delimiter : str, optional
        Character used to separate fields. Defaults to ','.
    encoding : str, optional
        File encoding. Defaults to 'utf-8'.
    index : bool, optional
        Whether to write row indices. Defaults to True.
    header : bool, optional
        Whether to write column names. Defaults to True.
    na_rep : str, optional
        String representation of NA/NaN values. Defaults to ''.
    """

    def __init__(
        self,
        delimiter: str = ",",
        encoding: str = "utf-8",
        index: bool = True,
        header: bool = True,
        na_rep: str = "",
    ) -> None:
        self.delimiter = delimiter
        self.encoding = encoding
        self.index = index
        self.header = header
        self.na_rep = na_rep

    def write(
        self,
        df: pd.DataFrame,
        filepath: str | Path,
        overwrite: bool = False,
    ) -> Path:
        """Write a DataFrame to a CSV file.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to write.
        filepath : str or Path
            Destination file path.
        overwrite : bool, optional
            If False and the file exists, raise FileExistsError. Defaults to False.

        Returns
        -------
        Path
            The path to the written file.

        Raises
        ------
        FileExistsError
            If the file exists and overwrite is False.
        """
        path = Path(filepath)

        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}")

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(
            path,
            sep=self.delimiter,
            encoding=self.encoding,
            index=self.index,
            header=self.header,
            na_rep=self.na_rep,
        )

        return path
