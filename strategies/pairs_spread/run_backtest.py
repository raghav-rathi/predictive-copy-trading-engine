"""Backtest runner for the pairs_spread strategy.

Paper only. Uses the LOCAL candle cache only
(data/candles/{BTC,ETH}_1h.csv); never calls fetch_candles.

Window (fixed, re-derived): t in [1773525600000, 1794574800000) =
2026-03-14 22:00 UTC -> 2026-11-13 13:00 UTC. Cached CSVs are filtered
to this window BEFORE indicators are computed.

This is a SINGLE spread book, not per-coin: the BTC and ETH legs
are combined into one synthetic spread instrument (see
indicators.build_spread_frame) and the standard harness runs ONCE
on it, starting from $10k.

Usage (from repo root):
    python3 strategies/pairs_spread/run_backtest.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pandas as pd

from strategies.pairs_spread import indicators, risk, signals
from strategies.backtest import run_backtest

START_MS = 1773525600000
END_MS = 1794574800000
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset="t", keep="first").sort_values("t")
    return df.reset_index(drop=True)


def main() -> None:
    btc = load_coin("BTC")
    eth = load_coin("ETH")
    spread = indicators.build_spread_frame(btc, eth)
    df = signals.add_signals(indicators.add_indicators(spread))
    res = run_backtest(df, risk.RISK, coin="SPREAD", interval="1h",
                       warmup=risk.WARMUP, use_funding=False)
    m = res.metrics()
    tr = res.trades
    wins = int((tr["net_pnl"] > 0).sum()) if len(tr) else 0
    reasons = tr["exit_reason"].value_counts().to_dict() if len(tr) else {}

    print(f"Window: t in [{START_MS}, {END_MS}) "
          f"(2026-03-14 22:00 UTC -> 2026-11-13 13:00 UTC)")
    print(f"Bar counts used: BTC {len(btc)}, ETH {len(eth)}, "
          f"spread bars {len(df)}")
    print()
    print("Single spread book (BTC-ETH synthetic spread instrument, "
          "$10k start):")
    print("| Instrument | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | PF |")
    print("|---|---|---|---|---|---|---|---|")
    print(f"| SPREAD | {m['trades']} | {100 * m['win_rate']:.1f}% | "
          f"{m['net_pnl_usd']:.2f} | {m['sharpe']:.2f} | "
          f"{m['max_dd_pct']:.1f}% | {m['expectancy_usd']:.2f} | "
          f"{m['profit_factor']:.2f} |")
    print(f"  exits SPREAD: {reasons}")
    print()
    print(f"Total fees: ${m['total_fees_usd']:.2f}")
    print(f"Sharpe: {m['sharpe']:.2f}, MaxDD: {m['max_dd_pct']:.2f}%")
    print(f"Start equity: $10000.00, end equity: ${res.meta['end_equity']:.2f}")


if __name__ == "__main__":
    main()
