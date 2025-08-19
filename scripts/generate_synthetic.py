from __future__ import annotations

import math
import random
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)


def business_days(start: str, periods: int) -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, periods=periods, tz=None)


def generate_prices(symbols: List[str], sectors: Dict[str, str], dates: pd.DatetimeIndex) -> pd.DataFrame:
    records: List[dict] = []
    for symbol in symbols:
        start_price = float(np.random.uniform(50.0, 300.0))
        daily_mu = 0.0005
        daily_sigma = 0.02
        prices = [start_price]
        vols = []
        vols_window = 20
        for i in range(1, len(dates)):
            r = float(np.random.normal(daily_mu, daily_sigma))
            prices.append(prices[-1] * (1.0 + r))
        prices = np.array(prices)
        # daily returns for volatility estimate
        rets = np.diff(prices) / prices[:-1]
        for i in range(len(dates)):
            if i == 0:
                vols.append(daily_sigma * math.sqrt(252.0))
            else:
                start = max(0, i - vols_window)
                window = rets[start:i]
                sigma = float(np.std(window)) if len(window) > 1 else daily_sigma
                vols.append(sigma * math.sqrt(252.0))

        volumes = (np.random.lognormal(mean=12.0, sigma=0.6, size=len(dates))).astype(int)

        for d, price, vol_est, volu in zip(dates, prices, vols, volumes):
            records.append(
                {
                    "date": pd.to_datetime(d).date(),
                    "ticker": symbol,
                    "sector": sectors.get(symbol, "Unknown"),
                    "close": round(float(price), 4),
                    "volume": int(volu),
                    "volatility": round(float(vol_est), 6),
                }
            )
    return pd.DataFrame.from_records(records)


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    prices_sorted = prices.sort_values(["ticker", "date"]).copy()
    prices_sorted["return"] = prices_sorted.groupby("ticker")["close"].pct_change()
    returns = prices_sorted.loc[:, ["date", "ticker", "return"]].dropna().reset_index(drop=True)
    return returns


def generate_headlines(symbols: List[str], dates: pd.DatetimeIndex) -> pd.DataFrame:
    headlines_samples = [
        "{sym} beats expectations amid strong demand",
        "{sym} misses guidance as costs rise",
        "Analysts turn optimistic on {sym}",
        "{sym} announces share buyback",
        "{sym} faces regulatory scrutiny",
        "{sym} unveils new product lineup",
        "{sym} reports record quarterly revenue",
        "Market remains cautious on {sym}",
    ]
    sources = ["Reuters", "Bloomberg", "CNBC", "WSJ"]

    rows: List[dict] = []
    for d in dates:
        for sym in symbols:
            # 35% chance of a headline per symbol per day
            if np.random.rand() < 0.35:
                headline = random.choice(headlines_samples).format(sym=sym)
                created_dt = datetime.combine(pd.to_datetime(d).date(), time(9, 30), tzinfo=timezone.utc)
                rows.append(
                    {
                        "date": pd.to_datetime(d).date(),
                        "symbol": sym,
                        "headline": headline,
                        "source": random.choice(sources),
                        "created_at": created_dt.isoformat().replace("+00:00", "Z"),
                    }
                )

    df = pd.DataFrame.from_records(rows, columns=["date", "symbol", "headline", "source", "created_at"])
    return df


def ensure_dirs() -> None:
    Path("data/raw").mkdir(parents=True, exist_ok=True)


def main() -> None:
    set_seed(42)
    ensure_dirs()

    # 4–8 symbols; choose 6 for a modest dataset
    symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA"]
    sectors = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOG": "Communication Services",
        "AMZN": "Consumer Discretionary",
        "META": "Communication Services",
        "NVDA": "Technology",
    }
    dates = business_days("2024-01-02", periods=70)

    prices = generate_prices(symbols, sectors, dates)
    returns = compute_returns(prices)
    headlines = generate_headlines(symbols, dates)

    prices.to_csv("data/raw/prices.csv", index=False)
    returns.to_csv("data/raw/returns.csv", index=False)
    headlines.to_csv("data/raw/headlines.csv", index=False)


if __name__ == "__main__":
    main()


