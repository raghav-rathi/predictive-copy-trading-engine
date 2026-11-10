"""Backtest Fisher ACD on the local 1h candle cache (paper only).

Window (fixed, re-derived): t in [1773525600000, 1794315600000)
= 2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC. Local cache only; no
network calls, no fetch_candles. $10k start per coin, funding off.

Combined metrics: the three coins' equity curves are reindexed to the
union of timestamps, forward-filled (leading gaps at $10k), summed into
a $30k curve; Sharpe (8760 bars/yr) and MaxDD are computed on that
summed curve. Combined trades = sum; combined win rate = total wins /
total trades; combined net = sum of nets; expectancy = combined net /
combined trades; profit factor = gross wins / gross losses across all
trades.

Usage: python3 -m strategies.fisher_acd.run_backtest
"""

import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies.backtest import run_backtest
from strategies.fisher_acd import indicators, risk, signals

START_MS = 1_773_525_600_000  # 2026-03-14 22:00 UTC
END_MS = 1_794_315_600_000    # 2026-11-10 13:00 UTC
COINS = ["BTC", "ETH", "HYPE"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="t", keep="first")
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].copy()
    df = df.sort_values("t").reset_index(drop=True)
    return df


def _sharpe_maxdd(equity: pd.Series, bars_per_year: int = 8760):
    rets = equity.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(bars_per_year)) if rets.std() > 0 else 0.0
    dd = (equity - equity.cummax()) / equity.cummax()
    return sharpe, float(dd.min() * 100)


def main():
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           start_equity=10_000.0, warmup=risk.WARMUP,
                           use_funding=False)
        m = res.metrics()
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        eq = res.equity.copy()
        eq.index = df["t"].to_numpy()
        results[coin] = {"metrics": m, "exits": exits, "equity": eq,
                         "trades": res.trades, "bars": len(df)}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={m['win_rate']*100:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxdd={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} pf={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined $30k curve.
    union_idx = sorted(set().union(*[set(r["equity"].index) for r in results.values()]))
    curves = []
    for coin in COINS:
        s = results[coin]["equity"].reindex(union_idx).ffill().fillna(10_000.0)
        curves.append(s)
    combined_eq = sum(curves)
    combined_sharpe, combined_maxdd = _sharpe_maxdd(combined_eq)

    all_trades = pd.concat([results[c]["trades"] for c in COINS], ignore_index=True)
    n = len(all_trades)
    wins = all_trades[all_trades["net_pnl"] > 0]
    gross_win = wins["net_pnl"].sum()
    gross_loss = -all_trades[all_trades["net_pnl"] <= 0]["net_pnl"].sum()
    combined_net = float(all_trades["net_pnl"].sum())
    total_fees = float(all_trades["fees_usd"].sum())
    pf = float(gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    print(f"COMBINED: bars_union={len(union_idx)} trades={n} "
          f"win%={100.0 * len(wins) / n if n else 0.0:.1f} net=${combined_net:.2f} "
          f"sharpe={combined_sharpe:.2f} maxdd={combined_maxdd:.1f}% "
          f"expectancy=${combined_net / n if n else 0.0:.2f} pf={pf:.2f} "
          f"fees=${total_fees:.2f} end_equity=${combined_eq.iloc[-1]:.2f}")

    # Machine-readable dump for BACKTEST.md.
    out = {
        coin: {
            "bars": results[coin]["bars"],
            "trades": int(results[coin]["metrics"]["trades"]),
            "win_rate": results[coin]["metrics"]["win_rate"],
            "net_pnl_usd": results[coin]["metrics"]["net_pnl_usd"],
            "sharpe": results[coin]["metrics"]["sharpe"],
            "max_dd_pct": results[coin]["metrics"]["max_dd_pct"],
            "expectancy_usd": results[coin]["metrics"]["expectancy_usd"],
            "profit_factor": results[coin]["metrics"]["profit_factor"],
            "total_fees_usd": results[coin]["metrics"]["total_fees_usd"],
            "exits": {str(k): int(v) for k, v in results[coin]["exits"].items()},
        }
        for coin in COINS
    }
    out["combined"] = {
        "trades": n,
        "win_rate": float(len(wins) / n) if n else 0.0,
        "net_pnl_usd": combined_net,
        "sharpe": combined_sharpe,
        "max_dd_pct": combined_maxdd,
        "expectancy_usd": combined_net / n if n else 0.0,
        "profit_factor": pf,
        "total_fees_usd": total_fees,
        "end_equity": float(combined_eq.iloc[-1]),
    }
    import json
    print("JSON:" + json.dumps(out))


if __name__ == "__main__":
    main()
