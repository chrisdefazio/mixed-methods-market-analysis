from __future__ import annotations

import argparse
import os
from pathlib import Path
from time import sleep
from typing import Callable, Optional

import pandas as pd
from dotenv import load_dotenv

try:
    # Imported for future use; no network calls are made here.
    from alpaca.data.historical import StockHistoricalDataClient  # type: ignore
    from alpaca.data.requests import StockBarsRequest  # type: ignore
except Exception:  # pragma: no cover - keep CLI usable even if API moves
    StockHistoricalDataClient = None  # type: ignore
    StockBarsRequest = None  # type: ignore


def retry(max_tries: int = 3, backoff_seconds: float = 1.0) -> Callable:
    """Simple retry decorator with fixed backoff.

    Args:
        max_tries: Maximum attempts.
        backoff_seconds: Sleep between attempts.
    """

    def decorator(fn: Callable[..., object]) -> Callable[..., object]:
        def wrapper(*args, **kwargs):
            tries = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception:  # noqa: BLE001 - CLI placeholder
                    tries += 1
                    if tries >= max_tries:
                        raise
                    sleep(backoff_seconds)

        return wrapper

    return decorator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch prices (structure only)")
    parser.add_argument("-symbols", type=str, required=True, help="CSV symbols e.g. AAPL,MSFT")
    parser.add_argument("-start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("-end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument("-timeframe", type=str, default="1Day", help="Bar timeframe (default 1Day)")
    parser.add_argument("-sector-map", type=str, default="", help="JSON path symbols->sector")
    return parser.parse_args()


def ensure_dirs() -> None:
    Path("data/raw").mkdir(parents=True, exist_ok=True)


def write_empty_outputs() -> None:
    """Write CSVs with headers only, matching the project schema."""

    prices_cols = ["date", "ticker", "sector", "close", "volume", "volatility"]
    returns_cols = ["date", "ticker", "return"]

    pd.DataFrame(columns=prices_cols).to_csv("data/raw/prices.csv", index=False)
    pd.DataFrame(columns=returns_cols).to_csv("data/raw/returns.csv", index=False)


def maybe_create_client() -> Optional[object]:
    """Instantiate Alpaca client if available and keys are set. No network calls."""

    api_key = os.getenv("APCA_API_KEY_ID")
    api_secret = os.getenv("APCA_API_SECRET_KEY")
    if not api_key or not api_secret or StockHistoricalDataClient is None:
        return None
    try:
        return StockHistoricalDataClient(api_key, api_secret)
    except Exception:
        return None


def main() -> None:
    load_dotenv()
    _ = parse_args()
    ensure_dirs()

    # Placeholder: structure only, no network calls yet.
    _client = maybe_create_client()

    write_empty_outputs()


if __name__ == "__main__":
    main()
