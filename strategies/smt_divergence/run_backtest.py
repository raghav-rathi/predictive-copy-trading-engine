"""Backtest runner for the smt_divergence strategy.

Paper only. Uses the LOCAL candle cache only
(data/candles/{BTC,ETH}_1h.csv); never calls fetch_candles.

Window (fixed, batch 40): t in [1773525600000, 1795096800000) =
2026-03-14 22:00 UTC -> 2026-11-19 14:00 UTC. Cached CSVs are filtered
to this window BEFORE indicators are computed.

Two-book structure: the strategy trades a pair, so it runs as TWO
separate $10k books -- book 1 trades BTC with ETH as the reference,
book 2 trades ETH with BTC as the reference. HYPE is excluded (no
pair). The Combined row pools both books ($20k start): pooled
trades / win rate / net / expectancy / profit factor, with Sharpe
and MaxDD computed on the summed $20k equity curve.

Usage (from repo root):
    python3 strategies/smt_divergence/run_backtest.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.smt_divergence import indicators, risk, signals
from strategies.backtest import run_backtest

START_MS = 1773525600000
END_MS = 1795096800000
BOOKS = [("BTC", "ETH"), ("ETH", "BTC")]  # (traded, reference)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.drop_duplicates(subset="t", keep="first").sort_values("t")
    return df.reset_index(drop=True)


def main() -> None:
    btc = load_coin("BTC")
    eth = load_coin("ETH")
    coins = {"BTC": btc, "ETH": eth}
    results = {}
    for traded, ref in BOOKS:
        merged = indicators.build_merged_frame(coins[traded], coins[ref])
        df = signals.add_signals(indicators.add_indicators(merged))
        res = run_backtest(df, risk.RISK, coin=traded, interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        results[f"{traded}/{ref}"] = (df, res)

    print(f"Window: t in [{START_MS}, {END_MS}) "
          f"(2026-03-14 22:00 UTC -> 2026-11-19 14:00 UTC)")
    print(f"Bar counts used: BTC {len(btc)}, ETH {len(eth)}")
    print()
    print("Two $10k books (traded / reference); HYPE excluded (no pair).")
    print("| Book | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | PF |")
    print("|---|---|---|---|---|---|---|---|")
    total_trades = 0
    total_wins = 0
    total_net = 0.0
    total_fees = 0.0
    gross_win = 0.0
    gross_loss = 0.0
    curves = {}
    for book, (df, res) in results.items():
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
        curves[book] = pd.Series(res.equity.to_numpy(),
                                 index=df["t"].to_numpy())
        reasons = (tr["exit_reason"].value_counts().to_dict()
                   if len(tr) else {})
        print(f"| {book} | {m['trades']} | {100 * m['win_rate']:.1f}% | "
              f"{m['net_pnl_usd']:.2f} | {m['sharpe']:.2f} | "
              f"{m['max_dd_pct']:.1f}% | {m['expectancy_usd']:.2f} | "
              f"{m['profit_factor']:.2f} |")
        print(f"  exits {book}: {reasons}")

    # Combined: sum the two $10k-start equity curves on the union of
    # timestamps (forward-fill, leading gaps at $10k) -> $20k curve.
    union_idx = sorted(set().union(*[set(s.index) for s in curves.values()]))
    summed = pd.Series(0.0, index=union_idx, dtype=float)
    for book in curves:
        s = curves[book].reindex(union_idx).ffill().fillna(10000.0)
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
    print(f"Combined start equity: $20000.00, end equity: ${summed.iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
