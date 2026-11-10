"""Backtest runner for Connors Double 7s (batch 32).

Loads the LOCAL candle cache only (data/candles/{BTC,ETH,HYPE}_1h.csv),
filters to the fixed window, runs the strategy per coin with
use_funding=False and start_equity=10000, and prints per-coin +
combined metrics. No network calls, no cache extension.

Run from the repo root:
    python3 strategies/connors_double_sevens/run_backtest.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.backtest import run_backtest
from strategies.connors_double_sevens import indicators, risk, signals

START_MS = 1_773_525_600_000  # 2026-03-14 22:00 UTC
END_MS = 1_794_315_600_000    # 2026-11-10 13:00 UTC (exclusive)
COINS = ["BTC", "ETH", "HYPE"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="t", keep="first")
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].copy()
    df = df.sort_values("t").reset_index(drop=True)
    return df


def main():
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False,
                           start_equity=10_000.0)
        m = res.metrics()
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        results[coin] = (res, m, exits)
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={m['win_rate'] * 100:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxdd={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined: sum the three $10k equity curves (reindex to the union
    # of timestamps, forward-fill, sum -> $30k curve).
    summed = None
    for coin, (res, _, _) in results.items():
        df = load_coin(coin)
        s = pd.Series(res.equity.to_numpy(),
                      index=pd.to_datetime(df["t"], unit="ms", utc=True))
        summed = s if summed is None else summed.add(s, fill_value=np.nan)
    summed = summed.ffill().fillna(30_000.0)
    rets = summed.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    dd = (summed - summed.cummax()) / summed.cummax()
    all_trades = pd.concat([r.trades for r, _, _ in results.values()],
                           ignore_index=True) if any(len(r.trades) for r, _, _ in results.values()) else pd.DataFrame()
    n = len(all_trades)
    wins = all_trades[all_trades["net_pnl"] > 0] if n else all_trades
    gross_win = wins["net_pnl"].sum() if n else 0.0
    gross_loss = -all_trades[all_trades["net_pnl"] <= 0]["net_pnl"].sum() if n else 0.0
    pf = float(gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    total_fees = sum(m["total_fees_usd"] for _, m, _ in results.values())
    print(f"COMBINED: trades={n} win%={100.0 * len(wins) / n if n else 0.0:.1f} "
          f"net=${sum(m['net_pnl_usd'] for _, m, _ in results.values()):.2f} "
          f"sharpe={sharpe:.2f} maxdd={float(dd.min() * 100):.1f}% "
          f"expectancy=${float(all_trades['net_pnl'].mean()) if n else 0.0:.2f} "
          f"PF={pf:.2f} fees=${total_fees:.2f} "
          f"end_equity=${float(summed.iloc[-1]):.2f}")


if __name__ == "__main__":
    main()
