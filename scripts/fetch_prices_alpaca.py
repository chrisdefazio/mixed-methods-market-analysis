from __future__ import annotations

import argparse
import os
from pathlib import Path
from time import sleep
from typing import Callable, Optional

import pandas as pd
from dotenv import load_dotenv

try:
    # alpaca-py v0.19 API
    from alpaca.data.historical import StockHistoricalDataClient  # type: ignore
    from alpaca.data.requests import StockBarsRequest  # type: ignore
    from alpaca.data.timeframe import TimeFrame  # type: ignore
except Exception:  # pragma: no cover - tolerate import issues in non-network envs
    StockHistoricalDataClient = None  # type: ignore
    StockBarsRequest = None  # type: ignore
    TimeFrame = None  # type: ignore


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


def compute_volatility_and_returns(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute rolling volatility (20-day, annualized) and simple returns.

    Args:
        df: Bars with columns [date, ticker, close, volume].

    Returns:
        Tuple of (prices_with_volatility, returns).
    """

    out = df.sort_values(["ticker", "date"]).copy()
    # daily simple returns for returns.csv
    out["return"] = out.groupby("ticker")["close"].pct_change()

    # rolling 20d std of returns, annualized
    rolling = out.groupby("ticker")["return"].rolling(20).std().reset_index(level=0, drop=True)
    vol = rolling * (252.0**0.5)
    out["volatility"] = vol.bfill().fillna(0.0)

    prices = out[["date", "ticker", "sector", "close", "volume", "volatility"]].copy()
    returns = out[["date", "ticker", "return"]].dropna().copy()
    return prices, returns


def maybe_create_client() -> Optional[object]:
    """Instantiate Alpaca client if available and keys are set."""

    api_key = os.getenv("APCA_API_KEY_ID")
    api_secret = os.getenv("APCA_API_SECRET_KEY")
    if not api_key or not api_secret or StockHistoricalDataClient is None:
        return None
    try:
        return StockHistoricalDataClient(api_key, api_secret)
    except Exception:
        return None


def fetch_bars_dataframe(
    client: object,
    symbols: list[str],
    start: str,
    end: str,
    timeframe: str,
    adjustment: str,
    feed: str,
) -> pd.DataFrame:
    """Fetch daily bars and return a flattened DataFrame for specified symbols.

    Uses alpaca-py `get_stock_bars` and consolidates multi-index to tidy rows.
    """

    if StockBarsRequest is None or TimeFrame is None:
        return pd.DataFrame()

    tf = TimeFrame.Day if timeframe.lower() in {"1d", "1day", "day"} else TimeFrame.Day
    req = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=tf,
        start=start,
        end=end,
        adjustment=adjustment,
        feed=feed,
        limit=10000,
    )
    resp = client.get_stock_bars(req)
    # resp.df is a MultiIndex (symbol, timestamp) DataFrame with ohlcv columns
    if not hasattr(resp, "df"):
        return pd.DataFrame()

    df = resp.df.reset_index()
    # Normalize columns: symbol -> ticker, timestamp -> date
    df = df.rename(columns={"symbol": "ticker", "timestamp": "date"})
    # Ensure close/volume columns exist whether API provided shorthand or long names
    if "c" in df.columns and "close" not in df.columns:
        df = df.rename(columns={"c": "close"})
    if "v" in df.columns and "volume" not in df.columns:
        df = df.rename(columns={"v": "volume"})
    # Only keep required fields if present
    keep = ["date", "ticker", "close", "volume"]
    df = df[[c for c in keep if c in df.columns]]
    # Add sector fallback
    df["sector"] = "Unknown"
    # Convert date to date (without time)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def main() -> None:
    load_dotenv()
    args = parse_args()
    ensure_dirs()

    client = maybe_create_client()
    data_feed = os.getenv("APCA_DATA_FEED", "sip")
    adjustment = os.getenv("APCA_ADJUSTMENT", "all")

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    if client is None:
        # No keys or client; write headers only
        write_empty_outputs()
        return

    # Fetch bars and compute outputs
    bars_df = fetch_bars_dataframe(
        client,
        symbols=symbols,
        start=args.start,
        end=args.end,
        timeframe=args.timeframe,
        adjustment=adjustment,
        feed=data_feed,
    )

    if bars_df.empty:
        write_empty_outputs()
        return

    prices_df, returns_df = compute_volatility_and_returns(bars_df)
    prices_df.to_csv("data/raw/prices.csv", index=False)
    returns_df.to_csv("data/raw/returns.csv", index=False)


if __name__ == "__main__":
    main()
