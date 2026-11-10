"""Backtest runner for Polarized Fractal Efficiency (batch 32).

Paper only. Uses the LOCAL candle cache only -- no network calls.
Window: t in [1773525600000, 1794315600000)
  = 2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC.
Per coin: $10k start, use_funding=False, warmup = risk.WARMUP.
Combined metrics: sum the three coins' equity curves (each $10k
start; reindex each to the union of timestamps, forward-fill, sum
-> $30k curve); Sharpe (8760 bars/yr) and MaxDD on the summed curve;
combined trades = sum; combined win rate = total wins / total trades;
combined net = sum of nets; expectancy = combined net / combined
trades; profit factor = gross wins / gross losses across all trades.

Run from the repo root:
    python3 strategies/polarized_fractal_efficiency/run_backtest.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.backtest import run_backtest
from strategies.polarized_fractal_efficiency import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_window(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset="t", keep="first").sort_values("t").reset_index(drop=True)
    return df


def main() -> dict:
    results = {}
    for coin in COINS:
        df = load_window(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False,
                           start_equity=10000.0)
        m = res.metrics()
        results[coin] = (res, m, len(df))
        exits = (res.trades["exit_reason"].value_counts().to_dict()
                 if len(res.trades) else {})
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * m['win_rate']:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined: sum equity curves on the union of timestamps.
    curves = []
    all_trades = []
    for coin in COINS:
        res, _, _ = results[coin]
        # Rebuild the timestamp index from the windowed frame.
        df = load_window(coin)
        eq = pd.Series(res.equity.to_numpy(), index=df["t"].to_numpy())
        curves.append(eq)
        if len(res.trades):
            all_trades.append(res.trades)
    union_idx = curves[0].index.union(curves[1].index).union(curves[2].index)
    summed = pd.Series(0.0, index=union_idx)
    for eq in curves:
        summed = summed + eq.reindex(union_idx).ffill().fillna(10000.0)
    rets = summed.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    roll_max = summed.cummax()
    max_dd = float(((summed - roll_max) / roll_max).min() * 100)
    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    n_trades = len(trades)
    wins = trades[trades["net_pnl"] > 0] if n_trades else trades
    gross_win = float(wins["net_pnl"].sum()) if n_trades else 0.0
    gross_loss = float(-trades[trades["net_pnl"] <= 0]["net_pnl"].sum()) if n_trades else 0.0
    combined = {
        "trades": n_trades,
        "win_rate": float(len(wins) / n_trades) if n_trades else 0.0,
        "net_pnl_usd": float(trades["net_pnl"].sum()) if n_trades else 0.0,
        "sharpe": sharpe,
        "max_dd_pct": max_dd,
        "expectancy_usd": float(trades["net_pnl"].mean()) if n_trades else 0.0,
        "profit_factor": float(gross_win / gross_loss) if gross_loss > 0
                         else (float("inf") if gross_win > 0 else 0.0),
        "total_fees_usd": float(trades["fees_usd"].sum()) if n_trades else 0.0,
    }
    print(f"COMBINED: trades={combined['trades']} "
          f"win%={100 * combined['win_rate']:.1f} "
          f"net=${combined['net_pnl_usd']:.2f} sharpe={combined['sharpe']:.2f} "
          f"maxDD={combined['max_dd_pct']:.1f}% "
          f"expectancy=${combined['expectancy_usd']:.2f} "
          f"PF={combined['profit_factor']:.2f} "
          f"fees=${combined['total_fees_usd']:.2f}")
    print(f"Bars used: " + ", ".join(f"{c} {results[c][2]}" for c in COINS))
    return {"per_coin": {c: results[c][1] for c in COINS},
            "combined": combined,
            "bars": {c: results[c][2] for c in COINS}}


if __name__ == "__main__":
    main()
