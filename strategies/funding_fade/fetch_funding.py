#!/usr/bin/env python3
"""Fetch hourly Hyperliquid funding history into the local cache.

Posts {"type": "fundingHistory", "coin": COIN, "startTime": ...,
"endTime": ...} to https://api.hyperliquid.xyz/info in 30-day chunks
and writes data/funding/{COIN}_1h.csv with columns t,funding_rate.

Alignment note: the API returns a `time` stamp a few tens of ms past
the hour (e.g. 1773446400044), while the OHLCV candle grid is exactly
hour-aligned. Each funding row is therefore floored to the hour-open
ms ((time // 3_600_000) * 3_600_000) before being written, so it
merges 1:1 onto the candle grid. Rows are deduplicated on t (first
row wins) and sorted ascending.

Window: 2026-03-14 00:00 UTC (1773446400000) -> 2026-11-21 14:00 UTC
(1795269600000), the batch-43 pinned backtest window.

Usage: python3 strategies/funding_fade/fetch_funding.py [BTC ETH HYPE]

The CSVs under data/funding/ are LOCAL ONLY (git-ignored cache, like
data/candles/) — never commit them. strategies/funding_fade/
indicators.py raises a clear ValueError if the cache file for the
requested coin is missing.
"""

import json
import os
import sys
import time
import urllib.request

INFO_URL = "https://api.hyperliquid.xyz/info"
START_MS = 1773446400000  # 2026-03-14 00:00 UTC
END_MS = 1795269600000    # 2026-11-21 14:00 UTC
CHUNK_MS = 10 * 24 * 3600 * 1000  # 10 days per request: the API caps
# fundingHistory responses at ~500 rows, so a 30-day (720h) chunk
# silently returns only its first ~500 hours and leaves a ~220h gap.
# 10-day (240h) chunks stay well under the cap.


def fetch_chunk(coin: str, start_ms: int, end_ms: int) -> list[dict]:
    payload = json.dumps(
        {"type": "fundingHistory", "coin": coin,
         "startTime": start_ms, "endTime": end_ms}
    ).encode()
    req = urllib.request.Request(
        INFO_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read().decode())
    return rows


def fetch_funding(coin: str, start_ms: int = START_MS,
                  end_ms: int = END_MS) -> list[tuple[int, float]]:
    """Return sorted, deduplicated [(hour-open ms, funding_rate)] pairs."""
    out: dict[int, float] = {}
    cur = start_ms
    while cur < end_ms:
        chunk_end = min(cur + CHUNK_MS, end_ms)
        rows = fetch_chunk(coin, cur, chunk_end)
        for r in rows:
            if "fundingRate" not in r or "time" not in r:
                continue
            t_hour = (int(r["time"]) // 3_600_000) * 3_600_000
            if t_hour not in out:
                out[t_hour] = float(r["fundingRate"])
        time.sleep(0.2)
        cur = chunk_end
    return sorted(out.items())


def main() -> int:
    coins = sys.argv[1:] or ["BTC", "ETH", "HYPE"]
    root = os.path.join(os.path.dirname(__file__), "..", "..")
    out_dir = os.path.join(root, "data", "funding")
    os.makedirs(out_dir, exist_ok=True)
    for coin in coins:
        pairs = fetch_funding(coin)
        path = os.path.join(out_dir, f"{coin}_1h.csv")
        with open(path, "w") as f:
            f.write("t,funding_rate\n")
            for t_ms, rate in pairs:
                f.write(f"{t_ms},{rate:.10f}\n")
        print(f"{coin}: {len(pairs)} hourly rows -> {path}")
        if pairs:
            print(f"    first t={pairs[0][0]} last t={pairs[-1][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
