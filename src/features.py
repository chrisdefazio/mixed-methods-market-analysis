from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def compute_simple_returns(df_prices: pd.DataFrame) -> pd.DataFrame:
    """Compute simple daily returns per ticker if not already provided.

    Expects prices with columns: `date`, `ticker`, `close`.

    Args:
        df_prices: Prices DataFrame.

    Returns:
        DataFrame with columns `date`, `ticker`, `return`.
    """

    required_cols = {"date", "ticker", "close"}
    if not required_cols.issubset(df_prices.columns):
        missing = required_cols - set(df_prices.columns)
        raise ValueError(f"prices missing columns: {sorted(missing)}")

    df_sorted = df_prices.sort_values(["ticker", "date"]).copy()
    df_sorted["return"] = df_sorted.groupby("ticker")["close"].pct_change()
    returns = df_sorted.loc[:, ["date", "ticker", "return"]].dropna().reset_index(drop=True)
    return returns


def merge_datasets(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    headlines: pd.DataFrame,
) -> pd.DataFrame:
    """Merge prices, returns, and headlines into a single DataFrame.

    Merges on `date`+`ticker` (`symbol` in headlines is aligned to `ticker`).

    Args:
        prices: Prices with columns including `date`, `ticker`, `sector`.
        returns: Returns with columns `date`, `ticker`, `return`.
        headlines: News with columns `date`, `symbol`, `headline`.

    Returns:
        Merged DataFrame; multiple headlines per date/ticker are preserved.
    """

    p = prices.copy()
    r = returns.copy()
    h = headlines.copy()

    # Normalize column names for join
    if "symbol" in h.columns:
        h = h.rename(columns={"symbol": "ticker"})

    # Inner join returns into prices by date,ticker
    pr = pd.merge(p, r, on=["date", "ticker"], how="inner")

    # Left join headlines (may duplicate rows if multiple headlines per date/ticker)
    merged = pd.merge(h, pr, on=["date", "ticker"], how="left")
    return merged


def rule_based_sentiment(text: str) -> float:
    """Very simple rule-based sentiment score in [-1, 1].

    A minimal dictionary approach; not intended as a production model.
    """

    if not isinstance(text, str) or not text.strip():
        return 0.0

    text_l = text.lower()
    positive = [
        "beat",
        "growth",
        "surge",
        "record",
        "gain",
        "up",
        "strong",
        "bull",
        "optimistic",
    ]
    negative = [
        "miss",
        "loss",
        "decline",
        "drop",
        "down",
        "weak",
        "bear",
        "pessimistic",
        "layoff",
    ]

    score = 0
    for token in positive:
        if token in text_l:
            score += 1
    for token in negative:
        if token in text_l:
            score -= 1

    # Normalize to [-1, 1]
    if score == 0:
        return 0.0
    max_abs = max(len(positive), len(negative))
    return float(np.clip(score / max_abs, -1.0, 1.0))


def add_sentiment_scores(df_headlines: pd.DataFrame) -> pd.DataFrame:
    """Add `sentiment_score` column to headlines using rule-based scoring."""

    df = df_headlines.copy()
    df["sentiment_score"] = df["headline"].apply(rule_based_sentiment)
    return df


def sentiment_bin(score: float) -> Literal["neg", "neu", "pos"]:
    """Bin a sentiment score into negative/neutral/positive categories."""

    if score <= -0.2:
        return "neg"
    if score >= 0.2:
        return "pos"
    return "neu"


def add_sentiment_bins(df_with_scores: pd.DataFrame) -> pd.DataFrame:
    """Add `sentiment_bin` categorical column from `sentiment_score`."""

    df = df_with_scores.copy()
    df["sentiment_bin"] = df["sentiment_score"].apply(sentiment_bin)
    return df


def fit_pca_scaler(features: pd.DataFrame) -> StandardScaler:
    """Fit a StandardScaler for downstream PCA.

    Args:
        features: Numeric feature matrix as DataFrame.

    Returns:
        Fitted `StandardScaler`.
    """

    scaler = StandardScaler()
    scaler.fit(features.values)
    return scaler
