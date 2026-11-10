"""Backtest runner for the Initial Balance breakout strategy.

Local candle cache only (data/candles/{BTC,ETH,HYPE}_1h.csv); no network
calls, no fetch_candles. Fixed window t in [1773525600000, 1794315600000)
= 2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC. Duplicates dropped
(keep first). $10k start per coin, funding off.

Combined metrics: the three coins' equity curves (each $10k start)
reindexed to the union of timestamps, forward-filled (leading gaps at
$10k), summed to a $30k curve; Sharpe (8760 bars/yr) and MaxDD on the
summed curve; combined trades = sum; combined win rate = total wins /
total trades; combined net = sum of nets; expectancy = combined net /
combined trades; profit factor = gross wins / gross losses across all
trades.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.backtest import run_backtest
from strategies.initial_balance_breakout import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1794315600000
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
    all_trades = []
    curves = {}
    print(f"Window: t in [{START_MS}, {END_MS}) = "
          "2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC")
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           start_equity=10_000.0, warmup=risk.WARMUP,
                           use_funding=False)
        m = res.metrics()
        results[coin] = (res, m, len(df))
        all_trades.append(res.trades.assign(coin=coin))
        curves[coin] = pd.Series(res.equity.to_numpy(), index=df["t"].to_numpy())
        exits = (res.trades["exit_reason"].value_counts().to_dict()
                 if len(res.trades) else {})
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * m['win_rate']:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"exp=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    total_trades = len(trades)
    wins = trades[trades["net_pnl"] > 0] if total_trades else trades
    gross_win = float(wins["net_pnl"].sum()) if total_trades else 0.0
    gross_loss = float(-trades[trades["net_pnl"] <= 0]["net_pnl"].sum()) if total_trades else 0.0
    net = float(trades["net_pnl"].sum()) if total_trades else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    win_rate = float(len(wins) / total_trades) if total_trades else 0.0
    expectancy = net / total_trades if total_trades else 0.0
    total_fees = float(trades["fees_usd"].sum()) if total_trades else 0.0

    union = sorted(set().union(*[set(c.index) for c in curves.values()]))
    combined = pd.DataFrame(index=union)
    for coin, curve in curves.items():
        combined[coin] = curve.reindex(union).ffill().fillna(10_000.0)
    eq = combined.sum(axis=1)
    rets = eq.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    max_dd = float(((eq - eq.cummax()) / eq.cummax()).min() * 100)
    print(f"COMBINED: trades={total_trades} win%={100 * win_rate:.1f} "
          f"net=${net:.2f} sharpe={sharpe:.2f} maxDD={max_dd:.1f}% "
          f"exp=${expectancy:.2f} PF={pf:.2f} fees=${total_fees:.2f} "
          f"end_equity=${eq.iloc[-1]:.2f}")
    for coin in COINS:
        res = results[coin][0]
        exits = (res.trades["exit_reason"].value_counts().to_dict()
                 if len(res.trades) else {})
        print(f"EXITS {coin}: {exits}")


if __name__ == "__main__":
    main()
