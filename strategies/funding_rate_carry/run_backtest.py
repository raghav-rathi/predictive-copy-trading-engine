"""Backtest runner for funding_rate_carry on the local candle + funding cache.

Paper only. Loads data/candles/{BTC,ETH,HYPE}_1h.csv, drops duplicate
timestamps (keep first), filters to the fixed batch-48 window
t in [1773525600000, 1795788000000) (2026-03-14 22:00 UTC ->
2026-11-27 14:00 UTC exclusive, last bar 13:00 UTC), then runs
strategies.backtest.run_backtest per coin with use_funding=False
and $10k start equity.

Funding economics -- the funding accrual IS the edge, and the
harness with use_funding=False only measures price PnL, so this
runner also computes funding PnL per trade from the LOCAL cache
(data/funding/{COIN}_1h.csv, same rows the indicators merge):
for each closed trade, notional = entry_px * qty, rates = hourly
funding rates with t in [entry_t, exit_t), and funding_usd =
funding_pnl_usd(side, notional, rates) from strategies.backtest.
TOTAL per trade = harness net_pnl (price, net of fees) +
funding_usd. Per coin and combined the runner reports price PnL,
funding PnL, and TOTAL separately, with TOTAL as the headline.
Combined Sharpe/MaxDD are computed on the total: each coin's
equity curve gets each trade's funding_usd added at the trade's
exit bar (cumulative from that bar onward), then the three $10k
curves are combined the same way as the price-only runners
(union of timestamps, forward-fill, sum to a $30k curve). A
position still open at the window end contributes no funding
(it has no exit bar yet) and its price MTM stays in the harness
curve; see BACKTEST.md.

Usage (from repo root):
    python3 strategies/funding_rate_carry/run_backtest.py
"""

import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies.backtest import funding_pnl_usd, run_backtest
from strategies.funding_rate_carry import indicators, risk, signals

START_MS = 1773525600000
END_MS = 1795788000000
COINS = ["BTC", "ETH", "HYPE"]
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_DIR = os.path.join(ROOT, "data", "candles")
FUNDING_DIR = os.path.join(ROOT, "data", "funding")
HOUR_MS = 3_600_000


def load_coin(coin: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{coin}_1h.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates("t", keep="first").sort_values("t").reset_index(drop=True)
    df = df[(df["t"] >= START_MS) & (df["t"] < END_MS)].reset_index(drop=True)
    df.attrs["coin"] = coin
    return df


def load_funding(coin: str) -> dict[int, float]:
    path = os.path.join(FUNDING_DIR, f"{coin}_1h.csv")
    f = pd.read_csv(path)
    return {int(t): float(r) for t, r in zip(f["t"], f["funding_rate"])}


def trade_funding_usd(trade: dict, funding: dict[int, float]) -> float:
    """Funding PnL for one closed trade, from the local cache.

    Rates are the hourly funding rates with t in [entry_t, exit_t).
    Raises KeyError if a funding row in the range is missing (never
    silently filled).
    """
    rates = [funding[t] for t in range(int(trade["entry_t"]), int(trade["exit_t"]), HOUR_MS)]
    notional = float(trade["entry_px"]) * float(trade["qty"])
    return funding_pnl_usd(trade["side"], notional, rates)


def equity_with_funding(equity: pd.Series, trades: pd.DataFrame,
                        t_values: np.ndarray) -> pd.Series:
    """Harness equity curve with each trade's funding_usd added at its exit bar.

    ``trades`` must carry exit_t and funding_usd columns; the funding
    is added cumulatively from the exit bar onward (the trade's
    funding is realized when the trade closes).
    """
    adj = np.zeros(len(equity))
    t_to_idx = {int(t): i for i, t in enumerate(t_values)}
    for _, tr in trades.iterrows():
        idx = t_to_idx.get(int(tr["exit_t"]))
        if idx is not None:
            adj[idx:] += float(tr["funding_usd"])
    return equity + adj


def _sharpe_maxdd(equity: pd.Series, bars_per_year: int = 8760):
    rets = equity.pct_change().fillna(0)
    sharpe = float(rets.mean() / rets.std() * math.sqrt(bars_per_year)) if rets.std() > 0 else 0.0
    dd = (equity - equity.cummax()) / equity.cummax()
    return sharpe, float(dd.min() * 100)


def _summarize(trades: pd.DataFrame, pnl_col: str) -> dict:
    n = len(trades)
    wins = trades[trades[pnl_col] > 0] if n else trades
    gross_win = wins[pnl_col].sum() if n else 0.0
    gross_loss = -trades[trades[pnl_col] <= 0][pnl_col].sum() if n else 0.0
    return {
        "trades": n,
        "win_rate": float(len(wins) / n) if n else 0.0,
        "net_pnl": float(trades[pnl_col].sum()) if n else 0.0,
        "expectancy": float(trades[pnl_col].mean()) if n else 0.0,
        "profit_factor": float(gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0),
    }


def main() -> None:
    results = {}
    for coin in COINS:
        df = load_coin(coin)
        funding = load_funding(coin)
        df = signals.add_signals(indicators.add_indicators(df))
        res = run_backtest(df, risk.RISK, coin=coin, interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        trades = res.trades.copy()
        if len(trades):
            trades["funding_usd"] = [trade_funding_usd(tr.to_dict(), funding) for _, tr in trades.iterrows()]
            trades["total_pnl"] = trades["net_pnl"] + trades["funding_usd"]
        else:
            trades["funding_usd"] = pd.Series(dtype=float)
            trades["total_pnl"] = pd.Series(dtype=float)
        eq = res.equity.copy()
        eq.index = df["t"].to_numpy()
        eq_total = equity_with_funding(eq, trades, df["t"].to_numpy())
        m = res.metrics()
        tot = _summarize(trades, "total_pnl")
        sharpe_tot, maxdd_tot = _sharpe_maxdd(eq_total)
        exits = trades["exit_reason"].value_counts().to_dict() if len(trades) else {}
        results[coin] = {"metrics": m, "exits": exits, "equity": eq,
                         "equity_total": eq_total, "trades": trades,
                         "bars": len(df), "total": tot,
                         "sharpe_total": sharpe_tot, "maxdd_total": maxdd_tot,
                         "funding_pnl": float(trades["funding_usd"].sum()) if len(trades) else 0.0}
        print(f"{coin}: bars={len(df)} trades={m['trades']} "
              f"win%={100 * tot['win_rate']:.1f} price=${m['net_pnl_usd']:.2f} "
              f"funding=${results[coin]['funding_pnl']:.2f} "
              f"TOTAL=${tot['net_pnl']:.2f} "
              f"sharpe(total)={sharpe_tot:.2f} maxDD(total)={maxdd_tot:.1f}% "
              f"expectancy(total)=${tot['expectancy']:.2f} PF(total)={tot['profit_factor']:.2f} "
              f"fees=${m['total_fees_usd']:.2f} exits={exits}")

    # Combined: sum the three $10k TOTAL equity curves (reindex to the
    # union of timestamps, forward-fill, leading gaps at $10k).
    union = sorted(set().union(*[set(r["equity_total"].index) for r in results.values()]))
    curves = [r["equity_total"].reindex(union).ffill().fillna(10_000.0) for r in results.values()]
    summed = sum(curves)
    sharpe, maxdd = _sharpe_maxdd(summed)
    trades = pd.concat([results[c]["trades"] for c in COINS], ignore_index=True)
    if "total_pnl" not in trades.columns:
        trades = pd.DataFrame({"net_pnl": pd.Series(dtype=float),
                               "funding_usd": pd.Series(dtype=float),
                               "total_pnl": pd.Series(dtype=float),
                               "fees_usd": pd.Series(dtype=float)})
    tot = _summarize(trades, "total_pnl")
    price_net = float(trades["net_pnl"].sum())
    fund_net = float(trades["funding_usd"].sum())
    print(f"COMBINED: trades={tot['trades']} win%(total)={100 * tot['win_rate']:.1f} "
          f"price=${price_net:.2f} funding=${fund_net:.2f} "
          f"TOTAL=${tot['net_pnl']:.2f} sharpe(total)={sharpe:.2f} "
          f"maxDD(total)={maxdd:.1f}% "
          f"expectancy(total)=${tot['expectancy']:.2f} "
          f"PF(total)={tot['profit_factor']:.2f} "
          f"fees=${trades['fees_usd'].sum():.2f} "
          f"start=${summed.iloc[0]:.2f} end=${summed.iloc[-1]:.2f}")

    out = {
        coin: {
            "bars": results[coin]["bars"],
            "trades": int(results[coin]["metrics"]["trades"]),
            "win_rate_total": results[coin]["total"]["win_rate"],
            "price_pnl_usd": results[coin]["metrics"]["net_pnl_usd"],
            "funding_pnl_usd": results[coin]["funding_pnl"],
            "total_pnl_usd": results[coin]["total"]["net_pnl"],
            "sharpe_total": results[coin]["sharpe_total"],
            "max_dd_pct_total": results[coin]["maxdd_total"],
            "expectancy_total_usd": results[coin]["total"]["expectancy"],
            "profit_factor_total": results[coin]["total"]["profit_factor"],
            "total_fees_usd": results[coin]["metrics"]["total_fees_usd"],
            "exits": {str(k): int(v) for k, v in results[coin]["exits"].items()},
        }
        for coin in COINS
    }
    out["combined"] = {
        "trades": tot["trades"],
        "win_rate_total": tot["win_rate"],
        "price_pnl_usd": price_net,
        "funding_pnl_usd": fund_net,
        "total_pnl_usd": tot["net_pnl"],
        "sharpe_total": sharpe,
        "max_dd_pct_total": maxdd,
        "expectancy_total_usd": tot["expectancy"],
        "profit_factor_total": tot["profit_factor"],
        "total_fees_usd": float(trades["fees_usd"].sum()),
        "end_equity": float(summed.iloc[-1]),
    }
    print("JSON:" + json.dumps(out))


if __name__ == "__main__":
    main()
