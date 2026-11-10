"""Backtest runner for bw_market_facilitation_index (batch 32).

Loads the LOCAL candle cache only (data/candles/{BTC,ETH,HYPE}_1h.csv),
filters to the fixed window t in [1773525600000, 1794315600000)
(2026-03-14 22:00 UTC -> 2026-11-10 13:00 UTC), dedupes by timestamp
(keep first), runs indicators + signals + the shared harness per coin
with use_funding=False and $10k start, and prints per-coin metrics,
exit-reason counts, and combined metrics on the summed $30k equity
curve (each coin's curve reindexed to the union of timestamps,
forward-filled, leading gaps at $10k).

Paper only. No network calls, no cache extension.
"""

import math
import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from strategies.backtest import run_backtest  # noqa: E402
from strategies.bw_market_facilitation_index import indicators, risk, signals  # noqa: E402

START_MS = 1773525600000
END_MS = 1794315600000
COINS = ["BTC", "ETH", "HYPE"]


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(REPO_ROOT, "data", "candles", f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="t", keep="first")
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)]
    df = df.sort_values("t").reset_index(drop=True)
    return df


def main() -> None:
    results = {}
    frames = {}
    for coin in COINS:
        df = load_coin(coin)
        frames[coin] = df
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           start_equity=10_000.0, warmup=risk.WARMUP,
                           use_funding=False)
        results[coin] = res
        m = res.metrics()
        reasons = res.trades["exit_reason"].value_counts().to_dict() if len(res.trades) else {}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={m['win_rate'] * 100:.1f} net=${m['net_pnl_usd']:.2f} "
              f"sharpe={m['sharpe']:.2f} maxDD={m['max_dd_pct']:.1f}% "
              f"expectancy=${m['expectancy_usd']:.2f} PF={m['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={reasons}")

    # Combined: sum the three $10k equity curves on the union of timestamps.
    union = sorted(set().union(*[set(f["t"]) for f in frames.values()]))
    curves = []
    for coin in COINS:
        res = results[coin]
        s = pd.Series(res.equity.to_numpy(), index=frames[coin]["t"].to_numpy())
        s = s.reindex(union).ffill().fillna(10_000.0)
        curves.append(s)
    combined = sum(curves)
    rets = combined.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(8760)) if rets.std() > 0 else 0.0
    dd = (combined - combined.cummax()) / combined.cummax()
    all_trades = pd.concat([results[c].trades for c in COINS], ignore_index=True)
    n = len(all_trades)
    wins = all_trades[all_trades["net_pnl"] > 0]
    gross_win = wins["net_pnl"].sum()
    gross_loss = -all_trades[all_trades["net_pnl"] <= 0]["net_pnl"].sum()
    pf = float(gross_win / gross_loss) if gross_loss > 0 else float("inf") if gross_win > 0 else 0.0
    total_fees = sum(results[c].metrics()["total_fees_usd"] for c in COINS)
    print(f"COMBINED: trades={n} win%={len(wins) / n * 100:.1f} "
          f"net=${all_trades['net_pnl'].sum():.2f} sharpe={sharpe:.2f} "
          f"maxDD={dd.min() * 100:.1f}% "
          f"expectancy=${all_trades['net_pnl'].mean() if n else 0.0:.2f} "
          f"PF={pf:.2f} fees=${total_fees:.2f}")


if __name__ == "__main__":
    main()
