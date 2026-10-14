"""Funding-rate tilt indicators (perp-native).

Mechanism: Hyperliquid funding is paid hourly; positive rate = longs pay
shorts. Extreme positive funding = crowded longs (contrarian short);
extreme negative = crowded shorts (contrarian long). The z-score of the
hourly funding rate over a 7-day lookback defines the tilt.

Funding history comes from the public `fundingHistory` endpoint, merged
onto the 1h bars with an asof join. Pass a precomputed `funding` Series
(indexed by ms) to skip the network fetch (unit tests do this).
"""

import time

import pandas as pd

from strategies import base as B
from strategies.data import _post

FUND_Z_LOOKBACK_H = 168  # 7 days


def load_funding(coin: str, start_ms: int, end_ms: int) -> pd.Series:
    """Hourly funding rates as a Series indexed by ms. Retries on truncation."""
    rows: list[dict] = []
    chunk = 30 * 86_400_000
    cur = start_ms
    while cur < end_ms:
        nxt = min(cur + chunk, end_ms)
        for attempt in range(20):
            try:
                out = _post({"type": "fundingHistory", "coin": coin,
                             "startTime": cur, "endTime": nxt})
                rows.extend(out if isinstance(out, list) else [])
                break
            except Exception:
                if attempt == 19:
                    raise
                time.sleep(min(2 * (attempt + 1), 15))
        cur = nxt
        time.sleep(0.2)
    s = pd.Series(
        {int(r["time"]): float(r["fundingRate"]) for r in rows if "fundingRate" in r},
        dtype=float,
    ).sort_index()
    s.index.name = "t"
    return s


def add_indicators(df: pd.DataFrame, coin: str | None = None,
                   funding: pd.Series | None = None) -> pd.DataFrame:
    df = df.copy()
    if funding is None:
        if coin is None:
            raise ValueError("funding_tilt.add_indicators needs coin= or funding=")
        funding = load_funding(coin, int(df["t"].min()), int(df["t"].max()))
    # asof merge: each bar gets the latest funding print at/before its open
    funding.index.name = "t"
    fdf = funding.rename("funding").reset_index()
    df = pd.merge_asof(df.sort_values("t"), fdf.sort_values("t"),
                       on="t", direction="backward")
    mu = df["funding"].rolling(FUND_Z_LOOKBACK_H, min_periods=24).mean()
    sd = df["funding"].rolling(FUND_Z_LOOKBACK_H, min_periods=24).std()
    df["fund_z"] = (df["funding"] - mu) / sd.replace(0, float("nan"))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df.sort_values("t").reset_index(drop=True)
