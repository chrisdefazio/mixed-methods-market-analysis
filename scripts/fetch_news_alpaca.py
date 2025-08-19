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
    from alpaca.data.historical import NewsClient  # type: ignore
    from alpaca.data.requests import NewsRequest  # type: ignore
except Exception:  # pragma: no cover - keep CLI usable even if API moves
    NewsClient = None  # type: ignore
    NewsRequest = None  # type: ignore


def retry(max_tries: int = 3, backoff_seconds: float = 1.0) -> Callable[[Callable[..., object]], Callable[..., object]]:
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
    parser.add_argument("-symbols", type=str, required=True, help="Comma-separated symbols, e.g., AAPL,MSFT")
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
    """Instantiate Alpaca news client if available and keys are set. No calls."""

    api_key = os.getenv("APCA_API_KEY_ID")
    api_secret = os.getenv("APCA_API_SECRET_KEY")
    if not api_key or not api_secret or NewsClient is None:
        return None
    try:
        return NewsClient(api_key, api_secret)
    except Exception:
        return None


def main() -> None:
    load_dotenv()
    _ = parse_args()
    ensure_dirs()

    # Placeholder: structure only, no network calls yet.
    _client = maybe_create_client()

    write_empty_output()


if __name__ == "__main__":
    main()


