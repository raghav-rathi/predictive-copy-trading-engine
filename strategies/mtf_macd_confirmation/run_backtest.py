"""Backtest runner for mtf_macd_confirmation on the local candle cache.

Paper only. Loads data/candles/{BTC,ETH,HYPE}_1h.csv, drops duplicate
timestamps (keep first), filters to the fixed batch-48 window
t in [1773525600000, 1795788000000) (2026-03-14 22:00 UTC ->
2026-11-27 14:00 UTC exclusive, last bar 13:00 UTC), then runs
strategies.backtest.run_backtest per coin with use_funding=False
and $10k start equity.

Usage (from repo root):
    python3 strategies/mtf_macd_confirmation/run_backtest.py
"""

import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies.backtest import run_backtest
from strategies.mtf_macd_confirmation import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1795788000000
COINS = ["BTC", "ETH", "HYPE"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "candles")


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates("t", keep="first").sort_values("t").reset_index(drop=True)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].reset_index(drop=True)
    return df


def _sharpe_maxdd(equity: pd.Series, bars_per_year: int = 8760):
    rets = equity.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(bars_per_year)) if rets.std() > 0 else 0.0
    dd = (equity - equity.cummax()) / equity.cummax()
    return sharpe, float(dd.min() * 100)


def main() -> None:
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        exits = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        eq = res.equity.copy()
        eq.index = df["t"].to_numpy()
        results[coin] = {"metrics": m, "exits": exits, "equity": eq,
                         "trades": res.trades, "bars": len(df)}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * m['win_rate']:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined: sum the three $10k equity curves (reindex to the union
    # of timestamps, forward-fill, leading gaps at $10k) -> $30k curve.
    union = sorted(set().union(*[set(r["equity"].index) for r in results.values()]))
    curves = [r["equity"].reindex(union).ffill().fillna(10_000.0) for r in results.values()]
    summed = sum(curves)
    sharpe, maxdd = _sharpe_maxdd(summed)
    trades = pd.concat([results[c]["trades"] for c in COINS], ignore_index=True)
    if "net_pnl" not in trades.columns:  # zero trades on every coin
        trades = pd.DataFrame({"net_pnl": pd.Series(dtype=float),
                               "fees_usd": pd.Series(dtype=float)})
    n = len(trades)
    wins = trades[trades["net_pnl"] > 0]
    gross_win = wins["net_pnl"].sum()
    gross_loss = -trades[trades["net_pnl"] <= 0]["net_pnl"].sum()
    pf = gross_win / gross_loss if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    print(f"COMBINED: trades={n} win%={100 * len(wins) / n if n else 0.0:.1f} "
          f"net=${trades['net_pnl'].sum():.2f} sharpe={sharpe:.2f} "
          f"maxDD={maxdd:.1f}% "
          f"expectancy=${trades['net_pnl'].mean() if n else 0.0:.2f} "
          f"PF={pf:.2f} "
          f"fees=${trades['fees_usd'].sum():.2f} "
          f"start=${summed.iloc[0]:.2f} end=${summed.iloc[-1]:.2f}")

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
        "net_pnl_usd": float(trades["net_pnl"].sum()),
        "sharpe": sharpe,
        "max_dd_pct": maxdd,
        "expectancy_usd": float(trades["net_pnl"].mean()) if n else 0.0,
        "profit_factor": pf,
        "total_fees_usd": float(trades["fees_usd"].sum()),
        "end_equity": float(summed.iloc[-1]),
    }
    print("JSON:" + json.dumps(out))


if __name__ == "__main__":
    main()
