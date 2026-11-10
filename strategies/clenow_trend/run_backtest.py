"""Backtest runner for clenow_trend on the local candle cache.

Paper only. Loads data/candles/{BTC,ETH,HYPE}_1h.csv, drops duplicate
timestamps (keep first), filters to the fixed window
t in [1773525600000, 1794315600000) (2026-03-14 22:00 UTC ->
2026-11-10 13:00 UTC), then runs strategies.backtest.run_backtest
per coin with use_funding=False and $10k start equity.

Usage (from repo root):
    python3 strategies/clenow_trend/run_backtest.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.clenow_trend import indicators, risk, signals
from strategies.backtest import run_backtest

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join("data", "candles", f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates("t", keep="first").sort_values("t").reset_index(drop=True)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].reset_index(drop=True)
    return df


def main() -> None:
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        results[coin] = res
        m = res.metrics()
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * m['win_rate']:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined: sum the three $10k equity curves (reindex to the union
    # of timestamps, forward-fill, leading gaps at $10k) -> $30k curve.
    curves = []
    for coin in COINS:
        eq = results[coin].equity.copy()
        eq.index = load_coin(coin)["t"].to_numpy()
        curves.append(eq)
    union = sorted(set().union(*[set(c.index) for c in curves]))
    summed = pd.Series(0.0, index=union)
    for c in curves:
        summed = summed + c.reindex(union).ffill().fillna(10_000.0)
    rets = summed.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * np.sqrt(8760)) if rets.std() > 0 else 0.0
    dd = (summed - summed.cummax()) / summed.cummax()
    trades = pd.concat([results[c].trades for c in COINS], ignore_index=True)
    if "net_pnl" not in trades.columns:  # zero trades on every coin
        trades = pd.DataFrame({"net_pnl": pd.Series(dtype=float),
                               "fees_usd": pd.Series(dtype=float)})
    wins = trades[trades["net_pnl"] > 0]
    gross_win = wins["net_pnl"].sum()
    gross_loss = -trades[trades["net_pnl"] <= 0]["net_pnl"].sum()
    total_trades = len(trades)
    win_rate = 100 * len(wins) / total_trades if total_trades else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    print(f"COMBINED: trades={total_trades} win%={win_rate:.1f} "
          f"net=${trades['net_pnl'].sum():.2f} sharpe={sharpe:.2f} "
          f"maxDD={100 * dd.min():.1f}% "
          f"expectancy=${trades['net_pnl'].mean() if total_trades else 0.0:.2f} "
          f"PF={pf:.2f} "
          f"fees=${trades['fees_usd'].sum():.2f} "
          f"start=${summed.iloc[0]:.2f} end=${summed.iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
