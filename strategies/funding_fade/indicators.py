"""Negative-funding fade indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Funding merge: the OHLCV candles carry no funding series, so the
   per-coin hourly funding rate is read from the local cache
   data/funding/{COIN}_1h.csv (populated by fetch_funding.py from
   Hyperliquid fundingHistory) and merged 1:1 onto the candle grid
   (both hour-aligned ms timestamps). The coin comes from
   df.attrs["coin"], set by the backtest driver. If the cache file
   is missing, or df.attrs has no coin, or any bar in the window
   has no funding row, a clear ValueError is raised naming the fix
   (run fetch_funding.py) — the series is NEVER silently replaced
   with another coin's series or with zeros, because a wrong funding
   series would fabricate entries.
2. Turn detection: funding_neg_turn is True on the first bar with
   funding_rate < 0 after a bar with funding_rate >= 0.
3. ATR(14) for the risk layer.

Columns:

    funding_rate     -- hourly funding rate for this coin (longs pay
                        shorts when positive; shorts pay longs when
                        negative)
    funding_neg_turn -- True on the bar funding turns negative
    atr              -- Wilder ATR(14)

No lookahead: the merge is a same-bar join on t, the turn test
reads funding[i] and funding[i-1] only, and ATR reads bars <= i.

Test path: add_indicators(df, funding_df=<DataFrame with t and
funding_rate>) bypasses the cache file entirely, so unit tests stay
network-free and file-free.
"""

import os

import numpy as np
import pandas as pd

from strategies import base as B

_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "funding")


def _load_funding_csv(coin: str) -> pd.DataFrame:
    path = os.path.join(_CACHE_DIR, f"{coin}_1h.csv")
    if not os.path.exists(path):
        raise ValueError(
            f"funding_fade: no funding cache for coin {coin!r} at {path}. "
            "Run `python3 strategies/funding_fade/fetch_funding.py "
            f"{coin}` to populate data/funding/ (local cache, not committed)."
        )
    return pd.read_csv(path)


def add_indicators(df: pd.DataFrame, funding_df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = df.copy()
    if funding_df is None:
        coin = df.attrs.get("coin") if hasattr(df, "attrs") else None
        if not coin:
            raise ValueError(
                "funding_fade: df.attrs['coin'] is not set, so the funding "
                "series cannot be identified. The backtest driver sets "
                "df.attrs['coin']; for tests pass funding_df= explicitly."
            )
        funding_df = _load_funding_csv(coin)
    f = funding_df[["t", "funding_rate"]].copy()
    f["t"] = f["t"].astype("int64")
    merged = df.merge(f, on="t", how="left")
    if merged["funding_rate"].isna().any():
        n_missing = int(merged["funding_rate"].isna().sum())
        first = merged.loc[merged["funding_rate"].isna(), "t"].iloc[0]
        raise ValueError(
            f"funding_fade: {n_missing} candle bars have no funding row "
            f"(first missing t={first}). Re-run fetch_funding.py to refresh "
            "data/funding/; never fill missing funding with zeros."
        )
    df = merged
    rate = df["funding_rate"].to_numpy(dtype=float)
    prev = np.concatenate([[np.nan], rate[:-1]])
    df["funding_neg_turn"] = (rate < 0) & (prev >= 0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
