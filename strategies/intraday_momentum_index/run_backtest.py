"""Backtest runner for the Intraday Momentum Index strategy (batch 32).

Paper only. Uses the LOCAL candle cache only
(data/candles/{BTC,ETH,HYPE}_1h.csv); no network calls, no fetch_candles.

Window (fixed, re-derived): t in [1773525600000, 1794315600000) =
2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC. Each coin starts at $10k,
use_funding=False. Combined metrics are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

Usage (from repo root):
    python3 strategies/intraday_momentum_index/run_backtest.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.backtest import run_backtest
from strategies.intraday_momentum_index import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]
BARS_PER_YEAR = 8760


def load_window(coin: str) -> pd.DataFrame:
    path = os.path.join("data", "candles", f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset="t", keep="first").sort_values("t")
    return df.reset_index(drop=True)


def main() -> None:
    results = {}
    all_trades = []
    curves = {}
    for coin in COINS:
        df = load_window(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           start_equity=10000.0, warmup=risk.WARMUP,
                           use_funding=False)
        m = res.metrics()
        results[coin] = (len(df), m, res)
        curves[coin] = pd.Series(res.equity.to_numpy(), index=df["t"].to_numpy())
        if len(res.trades):
            all_trades.append(res.trades)
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * m['win_rate']:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined: sum the three $10k-start equity curves on the union of
    # timestamps (forward-filled, leading gaps at $10k).
    union = sorted(set().union(*[set(c.index) for c in curves.values()]))
    summed = None
    for coin in COINS:
        aligned = curves[coin].reindex(union).ffill().fillna(10000.0)
        summed = aligned if summed is None else summed + aligned
    rets = summed.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(BARS_PER_YEAR)) if rets.std() > 0 else 0.0
    dd = (summed - summed.cummax()) / summed.cummax()
    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    n = len(trades)
    wins = trades[trades["net_pnl"] > 0] if n else trades
    gross_win = float(wins["net_pnl"].sum()) if n else 0.0
    gross_loss = float(-trades[trades["net_pnl"] <= 0]["net_pnl"].sum()) if n else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    net = float(trades["net_pnl"].sum()) if n else 0.0
    print(f"COMBINED: trades={n} win%={100 * len(wins) / n if n else 0:.1f} "
          f"net=${net:.2f} sharpe={sharpe:.2f} maxDD={100 * dd.min():.1f}% "
          f"expectancy=${net / n if n else 0:.2f} PF={pf:.2f} "
          f"fees=${float(trades['fees_usd'].sum()) if n else 0:.2f} "
          f"end_equity=${float(summed.iloc[-1]):.2f}")


if __name__ == "__main__":
    main()
