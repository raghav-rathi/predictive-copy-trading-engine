"""Backtest runner for the Volume Zone Oscillator strategy (batch 32).

Paper only. Uses the LOCAL candle cache only
(data/candles/{BTC,ETH,HYPE}_1h.csv); never calls fetch_candles.
Fixed window t in [1773525600000, 1794315600000) =
2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC.
Run from the repo root:  python3 -m strategies.volume_zone_oscillator.run_backtest
"""

import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies.backtest import run_backtest
from strategies.volume_zone_oscillator import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join("data", "candles", f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="t", keep="first")
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.sort_values("t").reset_index(drop=True)
    return df


def main() -> None:
    results = {}
    all_trades = []
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           start_equity=10_000.0, warmup=risk.WARMUP,
                           use_funding=False)
        res.equity.index = df["t"].to_numpy()
        results[coin] = res
        m = res.metrics()
        reasons = (res.trades["exit_reason"].value_counts().to_dict()
                   if len(res.trades) else {})
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win_rate={m['win_rate']*100:.1f}% net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} max_dd={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} pf={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f}")
        print(f"  exits: {reasons}")
        if len(res.trades):
            all_trades.append(res.trades)

    # Combined: sum the three $10k equity curves (reindexed to the union
    # of timestamps, forward-filled) -> $30k curve.
    union_idx = sorted(set().union(*[set(r.equity.index) for r in results.values()]))
    combined = pd.Series(0.0, index=union_idx)
    for res in results.values():
        combined = combined + res.equity.reindex(union_idx).ffill().fillna(10_000.0)
    rets = combined.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    roll_max = combined.cummax()
    max_dd = float(((combined - roll_max) / roll_max).min() * 100)
    trades = pd.concat(all_trades) if all_trades else pd.DataFrame()
    n = len(trades)
    wins = trades[trades["net_pnl"] > 0] if n else trades
    gross_win = float(wins["net_pnl"].sum()) if n else 0.0
    gross_loss = float(-trades[trades["net_pnl"] <= 0]["net_pnl"].sum()) if n else 0.0
    net = float(trades["net_pnl"].sum()) if n else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    print(f"COMBINED: trades={n} win_rate={len(wins)/n*100:.1f}% "
          f"net=${net:.2f} sharpe={sharpe:.2f} max_dd={max_dd:.1f}% "
          f"expectancy=${net/n:.2f} pf={pf:.2f} "
          f"fees=${float(trades['fees_usd'].sum()) if n else 0.0:.2f}")
    print(f"COMBINED end equity: ${combined.iloc[-1]:.2f} "
          f"(start $30000.00)")


if __name__ == "__main__":
    main()
