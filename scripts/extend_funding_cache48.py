#!/usr/bin/env python3
"""Extend the local funding cache to the batch-48 window end.

Fetches Hyperliquid fundingHistory in 1-day chunks (24 rows each — the
API caps responses near ~500 rows and the endpoint intermittently
returns 429 / RemoteDisconnected, so small chunks + generous backoff
are what actually completes) and merges the new rows into
data/funding/{COIN}_1h.csv, deduplicated on the hour-open ms timestamp.

Window: from each CSV's current max t + 1h through 2026-11-27 14:00 UTC
(1795788000000, exclusive). Rows are floored to the hour open, matching
the candle grid, exactly as in strategies/funding_fade/fetch_funding.py.

Usage: python3 scripts/extend_funding_cache48.py [BTC ETH HYPE]

The CSVs under data/funding/ are LOCAL ONLY (git-ignored cache, like
data/candles/) — this script never commits them.
"""

import json
import os
import sys
import time
import urllib.request

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "strategies", "funding_fade"))
from fetch_funding import fetch_chunk  # noqa: E402

END_MS = 1795788000000  # 2026-11-27 14:00 UTC (exclusive)
CHUNK_MS = 24 * 3_600_000  # 1 day per request
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "funding")


def extend_coin(coin: str) -> tuple[int, int, int]:
    path = os.path.join(CACHE_DIR, f"{coin}_1h.csv")
    old = pd.read_csv(path)
    start = int(old["t"].max()) + 3_600_000
    rows: dict[int, float] = {}
    cur = start
    while cur < END_MS:
        chunk_end = min(cur + CHUNK_MS, END_MS)
        fetched = None
        for attempt in range(6):
            try:
                fetched = fetch_chunk(coin, cur, chunk_end)
                break
            except Exception:
                time.sleep(15 * (attempt + 1))
        if fetched is None:
            print(f"{coin}: chunk starting {cur} failed after retries; "
                  f"stopping with {len(rows)} new rows fetched")
            break
        for r in fetched:
            if "fundingRate" in r and "time" in r:
                t_hour = (int(r["time"]) // 3_600_000) * 3_600_000
                rows.setdefault(t_hour, float(r["fundingRate"]))
        time.sleep(8)
        cur = chunk_end
    new = pd.DataFrame(sorted(rows.items()), columns=["t", "funding_rate"])
    merged = pd.concat([old, new]).drop_duplicates("t").sort_values("t")
    merged.to_csv(path, index=False)
    return len(old), len(merged), int(merged["t"].max())


def main() -> int:
    coins = sys.argv[1:] or ["BTC", "ETH", "HYPE"]
    for coin in coins:
        before, after, max_t = extend_coin(coin)
        print(f"{coin}: funding rows {before} -> {after}, max t {max_t}, "
              f"new {after - before}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
