#!/usr/bin/env python3
"""Run a registered strategy's backtest on cached Hyperliquid candles.

Usage: python3 scripts/run_strategy_backtest.py <slug> [COIN ...]

Prints per-coin metrics and a combined summary. Paper only.
"""

import importlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strategies.backtest import run_backtest
from strategies.data import fetch_candles


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    slug = sys.argv[1]
    coins = sys.argv[2:] or ["BTC", "ETH"]
    mod = importlib.import_module(f"strategies.{slug}")
    spec = mod.SPEC
    out = {"strategy": slug, "coins": {}}
    for coin in coins:
        df = fetch_candles(coin, "1h", 365)
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
    # combined
    tot_trades = sum(c["trades"] for c in out["coins"].values())
    tot_pnl = sum(c["net_pnl_usd"] for c in out["coins"].values())
    print(f"=== {slug} combined: {tot_trades} trades, net PnL ${tot_pnl:.2f} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
