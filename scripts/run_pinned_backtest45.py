#!/usr/bin/env python3
"""Pinned-window backtest driver for batch 45.

Reads the LOCAL candle cache only (never hits the Hyperliquid API, never
extends the cache) and restricts bars to the batch window:
    2026-03-14 22:00 UTC (1773525600000) <= t < 2026-11-24 14:00 UTC (1795525200000); last bar 13:00 UTC (last fully closed bar at run time)
Cache in practice starts 2026-03-14 22:00 UTC (first available bar).

Usage: python3 scripts/run_pinned_backtest45.py <slug> [COIN ...]
Prints per-coin metrics and a combined summary as JSON on the last line.
Paper only. Funding not modeled (offline run).
"""

import importlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

from strategies.backtest import run_backtest

START_MS = 1773525600000  # 2026-03-14 22:00 UTC
END_MS = 1795525200000    # 2026-11-24 14:00 UTC (exclusive; last bar 13:00 UTC)
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "candles")


def load_cached(coin: str) -> pd.DataFrame:
    path = os.path.join(CACHE_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset="t").sort_values("t").reset_index(drop=True)
    df["t"] = df["t"].astype("int64")
    for col in ("o", "h", "l", "c", "v"):
        df[col] = df[col].astype(float)
    return df[["t", "o", "h", "l", "c", "v"]]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    slug = sys.argv[1]
    coins = sys.argv[2:] or ["BTC", "ETH", "HYPE"]
    mod = importlib.import_module(f"strategies.{slug}")
    spec = mod.SPEC
    out = {"strategy": slug, "window": {"start_ms": START_MS, "end_ms": END_MS},
           "coins": {}}
    for coin in coins:
        df = load_cached(coin)
        # Tag the frame so coin-aware indicators (e.g. funding_fade, which
        # merges a per-coin funding series) can identify their coin.
        # DataFrame.copy() preserves .attrs, so this survives add_indicators.
        df.attrs["coin"] = coin
        df = spec.add_indicators(df)
        df = spec.add_signals(df)
        res = run_backtest(
            df, spec.risk, coin=coin, interval="1h",
            warmup=spec.warmup_bars, use_funding=False,
        )
        m = res.metrics()
        m["bars"] = len(df)
        out["coins"][coin] = m
        print(f"--- {slug} / {coin}: {len(df)} bars ---")
        for k, v in m.items():
            print(f"    {k}: {v:.4f}" if isinstance(v, float) else f"    {k}: {v}")
    tot_trades = sum(c["trades"] for c in out["coins"].values())
    tot_pnl = sum(c["net_pnl_usd"] for c in out["coins"].values())
    tot_fees = sum(c["total_fees_usd"] for c in out["coins"].values())
    print(f"=== {slug} combined: {tot_trades} trades, net PnL ${tot_pnl:.2f}, "
          f"fees ${tot_fees:.2f} ===")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
