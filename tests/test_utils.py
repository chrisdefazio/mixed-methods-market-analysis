import os
import random
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils import load_headlines, set_seed, validate_columns


def test_validate_columns_pass_and_strict():
    df = pd.DataFrame(
        {
            "a": [1, 2],
            "b": [3, 4],
            "c": [5, 6],
        }
    )

    # Pass: required present
    validate_columns(df, ["a", "b"])  # should not raise

    # Strict: exact column set should pass
    validate_columns(df, ["a", "b", "c"], strict=True)

    # Strict: missing + extras should raise
    try:
        validate_columns(df, ["a", "b"], strict=True)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for extras in strict mode when not exact match")


def test_validate_columns_missing_raises():
    df = pd.DataFrame({"a": [1], "c": [2]})
    try:
        validate_columns(df, ["a", "b"])  # missing b
    except ValueError as e:
        assert "Missing required columns" in str(e)
    else:
        raise AssertionError("Expected ValueError for missing columns")


def test_set_seed_deterministic_random_and_numpy():
    set_seed(123)
    seq1 = [random.random() for _ in range(3)]
    arr1 = np.random.rand(3)

    set_seed(123)
    seq2 = [random.random() for _ in range(3)]
    arr2 = np.random.rand(3)

    assert seq1 == seq2
    assert np.allclose(arr1, arr2)
    assert os.environ.get("PYTHONHASHSEED") == "123"


def test_load_headlines_parses_dates(tmp_path: Path):
    csv_path = tmp_path / "headlines.csv"
    csv_path.write_text(
        "date,symbol,headline,source,created_at\n"
        "2024-01-02,AAPL,Apple beats expectations,Reuters,2024-01-02T13:45:00Z\n"
    )

    df = load_headlines(csv_path)
    assert not df.empty
    assert pd.api.types.is_datetime64_any_dtype(df["date"])  # parsed
    assert pd.api.types.is_datetime64_any_dtype(df["created_at"])  # parsed
    validate_columns(df, ["date", "symbol", "headline"])  # required present


def test_pure_transform_normalizes_mock_alpaca_news_payload():
    # Tiny mock payload resembling Alpaca news schema
    payload = [
        {
            "headline": "AAPL announces buyback",
            "symbols": ["AAPL"],
            "source": "alpaca",
            "created_at": "2024-01-03T14:00:00Z",
        },
        {
            "headline": "MSFT growth outlook strong",
            "symbols": ["MSFT", "AAPL"],
            "source": "alpaca",
            "created_at": "2024-01-03T15:30:00Z",
        },
    ]

    # Pure transform: explode by symbol, select/rename to schema
    rows = []
    for item in payload:
        for sym in item.get("symbols", []):
            rows.append(
                {
                    "date": pd.to_datetime(item["created_at"]).date(),
                    "symbol": sym,
                    "headline": item["headline"],
                    "source": item.get("source", ""),
                    "created_at": pd.to_datetime(item["created_at"]),
                }
            )

    df = pd.DataFrame.from_records(rows)

    # Validate schema
    validate_columns(df, ["date", "symbol", "headline"])  # required
    # Types
    assert pd.api.types.is_datetime64_any_dtype(df["created_at"])  # parsed
    assert df.shape[0] == 3  # AAPL (2) + MSFT (1)
