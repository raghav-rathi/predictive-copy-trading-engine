#!/usr/bin/env python3
"""Fetch and cache OHLCV candles from the Hyperliquid public API.

Endpoint: POST https://api.hyperliquid.xyz/info
Body: {"type": "candleSnapshot", "req": {"coin": ..., "interval": "1d"|"4h"|"1h",
                                        "startTime": ms, "endTime": ms}}
Max 5000 candles per request; 1h history is fetched in 6-month chunks.

Writes data/<COIN>_<INTERVAL>.json (list of dicts, oldest first).
Reuses cache files when present unless --refresh is passed.
"""
import json
import os
import sys
import time
import urllib.request

API = "https://api.hyperliquid.xyz/info"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

COINS = ["BTC", "ETH", "SOL", "HYPE", "DOGE", "XRP", "BNB",
         "ADA", "AVAX", "LINK", "NEAR", "ARB"]
INTERVALS = ["1d", "4h", "1h"]
WINDOW_DAYS = 365
CHUNK_DAYS = {"1d": 400, "4h": 400, "1h": 170}  # stay under 5000 candles/req


def fetch(coin, interval, start_ms, end_ms):
    body = json.dumps({"type": "candleSnapshot",
                       "req": {"coin": coin, "interval": interval,
                               "startTime": start_ms, "endTime": end_ms}}).encode()
    req = urllib.request.Request(API, data=body,
                                 headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                rows = json.load(resp)
            out = []
            for r in rows:
                out.append({"t": r["t"], "o": float(r["o"]), "h": float(r["h"]),
                            "l": float(r["l"]), "c": float(r["c"]),
                            "v": float(r["v"])})
            out.sort(key=lambda x: x["t"])
            return out
        except Exception as exc:  # noqa: BLE001 - retry transient failures
            print(f"  retry {attempt + 1} for {coin} {interval}: {exc}",
                  file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {coin} {interval}")


def load(coin, interval):
    path = os.path.join(DATA_DIR, f"{coin}_{interval}.json")
    with open(path) as fh:
        return json.load(fh)


def main(refresh=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - WINDOW_DAYS * 86400 * 1000
    summary = {}
    for coin in COINS:
        for interval in INTERVALS:
            path = os.path.join(DATA_DIR, f"{coin}_{interval}.json")
            if os.path.exists(path) and not refresh:
                candles = load(coin, interval)
                print(f"cache {coin} {interval}: {len(candles)} candles")
                summary[f"{coin}_{interval}"] = len(candles)
                continue
            chunk_ms = CHUNK_DAYS[interval] * 86400 * 1000
            all_c = []
            s = start_ms
            while s < now_ms:
                e = min(s + chunk_ms, now_ms)
                all_c.extend(fetch(coin, interval, s, e))
                s = e
                time.sleep(0.15)  # be polite to the public endpoint
            # dedup by timestamp (chunk boundaries can overlap)
            seen = {}
            for c in all_c:
                seen[c["t"]] = c
            all_c = sorted(seen.values(), key=lambda x: x["t"])
            with open(path, "w") as fh:
                json.dump(all_c, fh)
            print(f"fetched {coin} {interval}: {len(all_c)} candles "
                  f"({time.strftime('%Y-%m-%d', time.gmtime(all_c[0]['t'] / 1000))}"
                  f" -> {time.strftime('%Y-%m-%d', time.gmtime(all_c[-1]['t'] / 1000))})")
            summary[f"{coin}_{interval}"] = len(all_c)
    print(json.dumps(summary))


if __name__ == "__main__":
    main(refresh="--refresh" in sys.argv)
