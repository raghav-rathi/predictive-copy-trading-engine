"""Backtest runner for the Sperandeo 2B strategy (batch 32).

Local candle cache only -- no network calls. Window fixed a priori:
t in [1773525600000, 1794315600000) = 2026-03-14 22:00 UTC ->
2026-11-10 13:00 UTC. Per coin: $10k start, funding off.

Run from the repo root:
    python3 -m strategies.sperandeo_2b.run_backtest
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sperandeo_2b import indicators, risk, signals
from strategies.backtest import run_backtest

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin):
    df = pd.read_csv(os.path.join(DATA_DIR, f"{coin}_1h.csv"))
    df = df.drop_duplicates("t", keep="first").sort_values("t").reset_index(drop=True)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].reset_index(drop=True)
    return df


def combined_metrics(results, frames):
    """Sum the three $10k equity curves (reindexed to the union of
    timestamps, forward-filled, leading gaps at $10k) -> $30k curve."""
    curves = []
    for res, df in zip(results, frames):
        curves.append(pd.Series(res.equity.to_numpy(), index=df["t"].to_numpy()))
    union = curves[0].index.union(curves[1].index).union(curves[2].index)
    summed = sum(c.reindex(union).ffill().fillna(10_000.0) for c in curves)
    rets = summed.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    dd = (summed - summed.cummax()) / summed.cummax()
    all_trades = pd.concat([r.trades for r in results], ignore_index=True)
    n = len(all_trades)
    wins = all_trades[all_trades["net_pnl"] > 0]
    gross_win = wins["net_pnl"].sum() if n else 0.0
    gross_loss = -all_trades[all_trades["net_pnl"] <= 0]["net_pnl"].sum() if n else 0.0
    pf = float(gross_win / gross_loss) if gross_loss > 0 else float("inf") if gross_win > 0 else 0.0
    return {
        "trades": n,
        "win_rate": float(len(wins) / n) if n else 0.0,
        "net_pnl_usd": float(all_trades["net_pnl"].sum()) if n else 0.0,
        "sharpe": sharpe,
        "max_dd_pct": float(dd.min() * 100),
        "expectancy_usd": float(all_trades["net_pnl"].mean()) if n else 0.0,
        "profit_factor": pf,
        "total_fees_usd": float(all_trades["fees_usd"].sum()) if n else 0.0,
        "end_equity": float(summed.iloc[-1]),
    }


def main():
    results, frames, metrics = [], [], {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False,
                           start_equity=10_000.0)
        m = res.metrics()
        results.append(res)
        frames.append(df)
        metrics[coin] = m
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={m['win_rate'] * 100:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    comb = combined_metrics(results, frames)
    print(f"COMBINED: trades={comb['trades']} win%={comb['win_rate'] * 100:.1f} "
          f"net=${comb['net_pnl_usd']:.2f} sharpe={comb['sharpe']:.2f} "
          f"maxDD={comb['max_dd_pct']:.1f}% expectancy=${comb['expectancy_usd']:.2f} "
          f"PF={comb['profit_factor']:.2f} fees=${comb['total_fees_usd']:.2f} "
          f"end_equity=${comb['end_equity']:.2f}")
    return metrics, comb


if __name__ == "__main__":
    main()
