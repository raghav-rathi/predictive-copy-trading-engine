"""Hyperliquid candle data loader with disk cache.

Uses the public ``candleSnapshot`` info endpoint (no auth).  Candles are
cached under ``data/candles/<COIN>_<INTERVAL>.csv`` so backtests are
repeatable without hammering the API.

Contract: returns a DataFrame with columns t,o,h,l,c,v (t = ms int,
ascending, unique).
"""

from __future__ import annotations

import json
import os
import time
import urllib.request

import pandas as pd

INFO_URL = "https://api.hyperliquid.xyz/info"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "candles")

INTERVAL_MS = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
}

MAX_PER_CALL = 5000


def _post(payload: dict, timeout: int = 30) -> object:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        INFO_URL, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _fetch_window(coin: str, interval: str, start_ms: int, end_ms: int) -> list:
    payload = {
        "type": "candleSnapshot",
        "req": {"coin": coin, "interval": interval, "startTime": start_ms, "endTime": end_ms},
    }
    out = _post(payload)
    return out if isinstance(out, list) else []


def fetch_candles(
    coin: str,
    interval: str = "1h",
    lookback_days: int = 365,
    end_ms: int | None = None,
    use_cache: bool = True,
    pace_s: float = 0.2,
) -> pd.DataFrame:
    """Fetch OHLCV candles for a Hyperliquid perp coin.

    ``coin`` like "BTC", "ETH", "HYPE".  ``interval`` one of 1m/5m/15m/1h/4h/1d.
    Returns columns t,o,h,l,c,v with t in ms, ascending.
    """
    if interval not in INTERVAL_MS:
        raise ValueError(f"bad interval {interval}")
    step = INTERVAL_MS[interval]
    end = int(end_ms or time.time() * 1000)
    start = end - lookback_days * 86_400_000

    cache_path = os.path.join(CACHE_DIR, f"{coin}_{interval}.csv")
    if use_cache and os.path.exists(cache_path):
        df = pd.read_csv(cache_path)
        # extend cache forward if stale
        last_t = int(df["t"].max())
        if last_t < end - step:
            extra = fetch_candles(
                coin, interval, lookback_days, end, use_cache=False, pace_s=pace_s
            )
            extra = extra[extra["t"] > last_t]
            if len(extra):
                df = pd.concat([df, extra], ignore_index=True)
                df.to_csv(cache_path, index=False)
        return _clean(df)

    rows: list[dict] = []
    cur = start
    while cur < end:
        nxt = min(cur + MAX_PER_CALL * step, end)
        for attempt in range(4):
            try:
                rows.extend(_fetch_window(coin, interval, cur, nxt))
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(1.5 * (attempt + 1))
        cur = nxt
        time.sleep(pace_s)

    df = pd.DataFrame(
        [
            {
                "t": int(r["t"]),
                "o": float(r["o"]),
                "h": float(r["h"]),
                "l": float(r["l"]),
                "c": float(r["c"]),
                "v": float(r["v"]),
            }
            for r in rows
        ]
    )
    if use_cache and len(df):
        os.makedirs(CACHE_DIR, exist_ok=True)
        df.to_csv(cache_path, index=False)
    return _clean(df)


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset="t").sort_values("t").reset_index(drop=True)
    df["t"] = df["t"].astype("int64")
    for col in ("o", "h", "l", "c", "v"):
        df[col] = df[col].astype(float)
    return df[["t", "o", "h", "l", "c", "v"]]
