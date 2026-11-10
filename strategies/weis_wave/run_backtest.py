"""Weis Wave backtest runner (paper only, local candle cache only).

Window: t in [1773525600000, 1794315600000) = 2026-03-14 22:00 UTC ->
2026-11-10 13:00 UTC. Loads data/candles/{BTC,ETH,HYPE}_1h.csv, drops
duplicate timestamps (keep first), filters to the window BEFORE
indicators, then runs strategies.backtest.run_backtest per coin with
use_funding=False and start_equity=10000.

Combined metrics: the three coins' equity curves (each $10k start)
reindexed to the union of timestamps, forward-filled (leading gaps at
$10k), summed to a $30k curve; Sharpe (8760 bars/yr) and MaxDD on the
summed curve; combined trades = sum; combined win rate = total wins /
total trades; combined net = sum of nets; expectancy = combined net /
combined trades; profit factor = gross wins / gross losses across all
trades.

Usage: python3 -m strategies.weis_wave.run_backtest  (from repo root)
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pandas as pd

from strategies.backtest import run_backtest
from strategies.weis_wave import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "candles", f"{coin}_1h.csv"
    )
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="t", keep="first").sort_values("t")
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].reset_index(drop=True)
    return df


def main() -> None:
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(
            df, risk.RISK, coin=coin, interval="1h",
            warmup=risk.WARMUP, use_funding=False, start_equity=10_000.0,
        )
        results[coin] = (df, res)
        m = res.metrics()
        reasons = (
            res.trades["exit_reason"].value_counts().to_dict()
            if len(res.trades) else {}
        )
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win_rate={m['win_rate'] * 100:.1f}% net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} max_dd={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} pf={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={reasons}")

    # Combined: sum equity curves on the union of timestamps.
    curves = {}
    for coin, (df, res) in results.items():
        curves[coin] = pd.Series(res.equity.to_numpy(), index=df["t"].to_numpy())
    union_idx = sorted(set().union(*[set(s.index) for s in curves.values()]))
    combined = pd.DataFrame(index=union_idx, dtype=float)
    for coin, s in curves.items():
        combined[coin] = s.reindex(union_idx).ffill().fillna(10_000.0)
    total = combined.sum(axis=1)
    rets = total.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    max_dd = float(((total - total.cummax()) / total.cummax()).min() * 100)

    all_trades = pd.concat(
        [res.trades.assign(coin=c) for c, (_, res) in results.items()],
        ignore_index=True,
    ) if any(len(res.trades) for _, res in results.values()) else pd.DataFrame()
    n = len(all_trades)
    wins = all_trades[all_trades["net_pnl"] > 0] if n else all_trades
    gross_win = float(wins["net_pnl"].sum()) if n else 0.0
    gross_loss = float(-all_trades[all_trades["net_pnl"] <= 0]["net_pnl"].sum()) if n else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    total_fees = float(all_trades["fees_usd"].sum()) if n else 0.0
    total_net = float(all_trades["net_pnl"].sum()) if n else 0.0
    print(f"COMBINED: trades={n} win_rate={len(wins) / n * 100:.1f}% "
          f"net=${total_net:.2f} sharpe={sharpe:.2f} max_dd={max_dd:.1f}% "
          f"expectancy=${total_net / n:.2f} pf={pf:.2f} fees=${total_fees:.2f}")


if __name__ == "__main__":
    main()
