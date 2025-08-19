from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence, Union

import numpy as np
import pandas as pd

PathLike = Union[str, Path]


def set_seed(seed: int) -> None:
    """Set global random seeds for reproducibility.

    Sets seeds for the Python `random` module, NumPy, and `PYTHONHASHSEED`.

    Args:
        seed: Non-negative integer seed value.
    """

    if seed < 0:
        raise ValueError("seed must be non-negative")

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


def validate_columns(
    df: pd.DataFrame, required_columns: Iterable[str], *, strict: bool = False
) -> None:
    """Validate that a DataFrame contains required columns.

    Args:
        df: DataFrame to validate.
        required_columns: Columns that must be present in `df`.
        strict: If True, raise if `df` has columns outside `required_columns`.

    Raises:
        ValueError: If required columns are missing or extras present in strict mode.
    """

    data_columns: set[str] = set(df.columns)
    required: set[str] = set(required_columns)
    missing = required - data_columns
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if strict:
        extras = data_columns - required
        if extras:
            raise ValueError(f"Unexpected columns present: {sorted(extras)}")


def read_csv_safe(
    path: PathLike,
    *,
    parse_dates: Optional[Sequence[str]] = None,
    dtype: Optional[Dict[str, str]] = None,
    na_values: Optional[Sequence[str]] = ("", "NA", "NaN", "null"),
) -> pd.DataFrame:
    """Read a CSV file safely with consistent parsing.

    Handles missing files and empty files gracefully.

    Args:
        path: File path to read.
        parse_dates: Column names to parse as datetimes.
        dtype: Optional dtype mapping for columns.
        na_values: Additional strings to treat as NA.

    Returns:
        Parsed DataFrame (empty if the file exists but has no rows).

    Raises:
        FileNotFoundError: If the file does not exist.
        pd.errors.ParserError: If parsing fails for other reasons.
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    try:
        df = pd.read_csv(
            file_path,
            dtype=dtype,
            parse_dates=list(parse_dates) if parse_dates else None,
            na_values=list(na_values) if na_values else None,
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

    return df


def write_csv_safe(df: pd.DataFrame, path: PathLike, *, index: bool = False) -> None:
    """Write a DataFrame to CSV, ensuring parent directories exist.

    Args:
        df: DataFrame to write.
        path: Destination file path.
        index: Whether to write the index.
    """

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=index)


def load_prices(path: PathLike = "data/raw/prices.csv") -> pd.DataFrame:
    """Load prices data with schema validation.

    Expected columns: `date`, `ticker`, `sector`, `close`, `volume`, `volatility`.

    Args:
        path: CSV path (default `data/raw/prices.csv`).

    Returns:
        Validated prices DataFrame with `date` parsed as datetime.
    """

    df = read_csv_safe(path, parse_dates=["date"])
    if not df.empty:
        validate_columns(
            df,
            ["date", "ticker", "sector", "close", "volume", "volatility"],
        )
    return df


def load_returns(path: PathLike = "data/raw/returns.csv") -> pd.DataFrame:
    """Load returns data with schema validation.

    Expected columns: `date`, `ticker`, `return`.

    Args:
        path: CSV path (default `data/raw/returns.csv`).

    Returns:
        Validated returns DataFrame with `date` parsed as datetime.
    """

    df = read_csv_safe(path, parse_dates=["date"])
    if not df.empty:
        validate_columns(df, ["date", "ticker", "return"])
    return df


def load_headlines(path: PathLike = "data/raw/headlines.csv") -> pd.DataFrame:
    """Load headlines data with schema validation and date parsing.

    Required columns: `date`, `symbol`, `headline`.
    Optional columns: `source`, `created_at`.

    Args:
        path: CSV path (default `data/raw/headlines.csv`).

    Returns:
        Headlines DataFrame with `date` parsed, and `created_at` parsed if present.
    """

    # Parse both potential datetime columns if present
    df = read_csv_safe(path)
    if df.empty:
        return df

    required = ["date", "symbol", "headline"]
    validate_columns(df, required)

    # Parse dates if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df
