"""Backtest runner for the sinewave strategy.

Paper only. Uses the LOCAL candle cache only
(data/candles/{BTC,ETH,HYPE}_1h.csv); never calls fetch_candles.

Window (fixed, re-derived): t in [1773525600000, 1794488400000) =
2026-03-14 22:00 UTC -> 2026-11-12 13:00 UTC. Cached CSVs are filtered
to this window BEFORE indicators are computed.

Usage (from repo root):
    python3 strategies/sinewave/run_backtest.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sinewave import indicators, risk, signals
from strategies.backtest import run_backtest

START_MS = 1773525600000
END_MS = 1794488400000
COINS = ["BTC", "ETH", "HYPE"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset="t", keep="first").sort_values("t")
    return df.reset_index(drop=True)


def main() -> None:
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        results[coin] = (df, res)

    print(f"Window: t in [{START_MS}, {END_MS}) "
          f"(2026-03-14 22:00 UTC -> 2026-11-12 13:00 UTC)")
    print(f"Bar counts used: " + ", ".join(
        f"{c} {len(results[c][0])}" for c in COINS))
    print()
    print("| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | PF |")
    print("|---|---|---|---|---|---|---|---|")
    total_trades = 0
    total_wins = 0
    total_net = 0.0
    total_fees = 0.0
    gross_win = 0.0
    gross_loss = 0.0
    curves = {}
    for coin in COINS:
        df, res = results[coin]
        m = res.metrics()
        tr = res.trades
        wins = int((tr["net_pnl"] > 0).sum()) if len(tr) else 0
        gw = float(tr[tr["net_pnl"] > 0]["net_pnl"].sum()) if len(tr) else 0.0
        gl = float(-tr[tr["net_pnl"] <= 0]["net_pnl"].sum()) if len(tr) else 0.0
        total_trades += m["trades"]
        total_wins += wins
        total_net += m["net_pnl_usd"]
        total_fees += m["total_fees_usd"]
        gross_win += gw
        gross_loss += gl
        curves[coin] = pd.Series(res.equity.to_numpy(),
                                 index=df["t"].to_numpy())
        reasons = (tr["exit_reason"].value_counts().to_dict()
                   if len(tr) else {})
        print(f"| {coin} | {m['trades']} | {100 * m['win_rate']:.1f}% | "
              f"{m['net_pnl_usd']:.2f} | {m['sharpe']:.2f} | "
              f"{m['max_dd_pct']:.1f}% | {m['expectancy_usd']:.2f} | "
              f"{m['profit_factor']:.2f} |")
        print(f"  exits {coin}: {reasons}")

    # Combined: sum the three $10k-start equity curves on the union of
    # timestamps (forward-fill, leading gaps at $10k) -> $30k curve.
    union_idx = sorted(set().union(*[set(s.index) for s in curves.values()]))
    summed = pd.Series(0.0, index=union_idx, dtype=float)
    for coin in COINS:
        s = curves[coin].reindex(union_idx).ffill().fillna(10000.0)
        summed = summed + s
    rets = summed.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    roll_max = summed.cummax()
    max_dd = float(((summed - roll_max) / roll_max).min() * 100)
    comb_win_rate = total_wins / total_trades if total_trades else 0.0
    comb_expectancy = total_net / total_trades if total_trades else 0.0
    comb_pf = gross_win / gross_loss if gross_loss > 0 else (
        float("inf") if gross_win > 0 else 0.0)
    print(f"| **Combined** | **{total_trades}** | "
          f"**{100 * comb_win_rate:.1f}%** | **{total_net:.2f}** | "
          f"**{sharpe:.2f}** | **{max_dd:.1f}%** | "
          f"**{comb_expectancy:.2f}** | **{comb_pf:.2f}** |")
    print()
    print(f"Total fees: ${total_fees:.2f}")
    print(f"Combined Sharpe: {sharpe:.2f}, Combined MaxDD: {max_dd:.2f}%")
    print(f"Combined start equity: $30000.00, end equity: ${summed.iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
