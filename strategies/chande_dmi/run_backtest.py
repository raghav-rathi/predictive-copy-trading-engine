"""Backtest runner for Chande Dynamic Momentum Index (batch 32).

Loads the LOCAL candle cache only (data/candles/{BTC,ETH,HYPE}_1h.csv);
fetch_candles is never called, so the cache is not extended past the
window. Window t in [1773525600000, 1794315600000) =
2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC, duplicates dropped
(keep first). $10k start per coin, funding off.

Combined metrics: sum the three coins' equity curves (each $10k
start; reindex each to the union of timestamps, forward-fill, leading
gaps at $10k) -> $30k curve; Sharpe (8760 bars/yr) and MaxDD on the
summed curve; combined trades = sum; combined win rate = total
wins / total trades; combined net = sum of nets; expectancy =
combined net / combined trades; profit factor = gross wins /
gross losses across all trades.

Usage: python3 strategies/chande_dmi/run_backtest.py  (from repo root)
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.backtest import run_backtest
from strategies.chande_dmi import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]
START_EQUITY = 10_000.0


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join("data", "candles", f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset=["t"], keep="first").sort_values("t")
    return df.reset_index(drop=True)


def main():
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False,
                           start_equity=START_EQUITY)
        results[coin] = (df, res)
        m = res.metrics()
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * m['win_rate']:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxdd={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} pf={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined $30k curve: reindex each equity curve to the union of
    # timestamps, forward-fill, leading gaps at $10k, then sum.
    union = sorted(set().union(*[set(df["t"]) for df, _ in results.values()]))
    curves = []
    for coin in COINS:
        df, res = results[coin]
        s = pd.Series(res.equity.to_numpy(dtype=float), index=df["t"].to_numpy())
        s = s.reindex(union).ffill().fillna(START_EQUITY)
        curves.append(s)
    combined = sum(curves)
    rets = combined.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    roll_max = combined.cummax()
    max_dd = float(((combined - roll_max) / roll_max).min() * 100)

    all_trades = pd.concat([res.trades for _, res in results.values()], ignore_index=True)
    n = len(all_trades)
    wins = all_trades[all_trades["net_pnl"] > 0]
    gross_win = float(wins["net_pnl"].sum())
    gross_loss = float(-all_trades[all_trades["net_pnl"] <= 0]["net_pnl"].sum())
    net = float(all_trades["net_pnl"].sum())
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    total_fees = float(all_trades["fees_usd"].sum())
    print(f"COMBINED: trades={n} win%={100 * len(wins) / n:.1f} net=${net:.2f} "
          f"sharpe={sharpe:.2f} maxdd={max_dd:.1f}% "
          f"expectancy=${net / n:.2f} pf={pf:.2f} fees=${total_fees:.2f} "
          f"end_equity=${combined.iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
