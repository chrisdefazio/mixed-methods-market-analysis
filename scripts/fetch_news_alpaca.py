from __future__ import annotations

import argparse
import os
from pathlib import Path
from time import sleep
from typing import Callable, Optional

import pandas as pd
from dotenv import load_dotenv

try:
    from alpaca.data.historical import NewsClient  # type: ignore
    from alpaca.data.requests import NewsRequest  # type: ignore
except Exception:  # pragma: no cover
    NewsClient = None  # type: ignore
    NewsRequest = None  # type: ignore


def retry(max_tries: int = 3, backoff_seconds: float = 1.0) -> Callable:
    """Simple retry decorator with fixed backoff."""

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
    parser = argparse.ArgumentParser(description="Fetch market news (structure only)")
    parser.add_argument("-symbols", type=str, required=True, help="CSV symbols e.g. AAPL,MSFT")
    parser.add_argument("-start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("-end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument("-limit", type=int, default=1000, help="Max news items")
    return parser.parse_args()


def ensure_dirs() -> None:
    Path("data/raw").mkdir(parents=True, exist_ok=True)


def write_empty_output() -> None:
    """Write headlines CSV with headers only, matching the schema."""

    cols = ["date", "symbol", "headline", "source", "created_at"]
    pd.DataFrame(columns=cols).to_csv("data/raw/headlines.csv", index=False)


def maybe_create_client() -> Optional[object]:
    """Instantiate Alpaca news client if available and keys are set."""

    api_key = os.getenv("APCA_API_KEY_ID")
    api_secret = os.getenv("APCA_API_SECRET_KEY")
    if not api_key or not api_secret or NewsClient is None:
        return None
    try:
        return NewsClient(api_key, api_secret)
    except Exception:
        return None


def fetch_news_dataframe(
    client: object,
    symbols: list[str],
    start: str,
    end: str,
    limit: int,
) -> pd.DataFrame:
    """Fetch news with pagination and normalize to headlines schema.

    Endpoint: /v1beta1/news via alpaca-py NewsClient.get_news
    """

    if NewsRequest is None:
        return pd.DataFrame()

    rows = []
    page_token = None
    while True:
        req = NewsRequest(
            symbols=symbols,
            start=start,
            end=end,
            limit=limit,
            page_token=page_token,
        )
        resp = client.get_news(req)
        items = getattr(resp, "news", [])
        for item in items:
            # item may be a pydantic model; use getattr defensively
            headline = getattr(item, "headline", "")
            syms = getattr(item, "symbols", []) or []
            created_at = getattr(item, "created_at", None)
            source = getattr(item, "source", "")
            for sym in syms:
                rows.append(
                    {
                        "date": pd.to_datetime(created_at).date() if created_at else None,
                        "symbol": sym,
                        "headline": headline,
                        "source": source,
                        "created_at": pd.to_datetime(created_at) if created_at else None,
                    }
                )
        page_token = getattr(resp, "next_page_token", None)
        if not page_token:
            break
        sleep(0.05)

    df = pd.DataFrame.from_records(
        rows, columns=["date", "symbol", "headline", "source", "created_at"]
    )
    return df


def main() -> None:
    load_dotenv()
    args = parse_args()
    ensure_dirs()

    client = maybe_create_client()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    if client is None:
        write_empty_output()
        return

    df = fetch_news_dataframe(
        client,
        symbols=symbols,
        start=args.start,
        end=args.end,
        limit=args.limit,
    )
    if df.empty:
        write_empty_output()
        return
    df.to_csv("data/raw/headlines.csv", index=False)


if __name__ == "__main__":
    main()
