#!/usr/bin/env python3
"""Empirical check: run the flow filter over the live paper targets.

Fetches trailing-30d fills for each address in paper/paper_targets.json
and reports flow flags. Answers: does the filter fire on anything we're
currently copying, and would it have changed any live decision?
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hyperliquid"))

from flow_filter import is_uncopyable
from scorer import HyperliquidInfo

DAY_MS = 86_400_000


def main() -> int:
    with open("paper/paper_targets.json") as f:
        wallets = json.load(f)["wallets"]
    info = HyperliquidInfo("https://api.hyperliquid.xyz/info", pace_s=0.5)
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - 30 * DAY_MS
    print(f"{'target':22s} {'fills':>6s}  flags")
    print("-" * 50)
    flagged = 0
    for w in wallets:
        addr = w["address"]
        label = w.get("label", addr[:10])
        try:
            fills = info.user_fills_by_time(addr, start_ms, end_ms)
        except Exception as e:  # noqa: BLE001 - one bad fetch must not kill it
            print(f"{label:22s} {'ERR':>6s}  {e}")
            continue
        # scorer counts closes; approximate with close fills here
        n_closes = sum(1 for x in fills
                       if str(x.get("dir", "")).startswith("Close"))
        flags, m = is_uncopyable(fills, n_closes)
        mark = "  <-- FLAGGED" if flags else ""
        if flags:
            flagged += 1
        print(f"{label:22s} {len(fills):>6d}  {','.join(flags) or '-'}"
              f"  ({m['trades_per_hour']}/h, hold {m['avg_hold_s']}s,"
              f" flips {m['flip_count']}){mark}")
    print("-" * 50)
    print(f"{flagged}/{len(wallets)} targets flagged uncopyable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
