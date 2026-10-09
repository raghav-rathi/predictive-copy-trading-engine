"""Event-driven backtest harness for strategy engines.

Execution model (no lookahead):
  * signals are boolean columns produced by the strategy on bar i
  * entries/exits on signal execute at bar i+1 open
  * risk exits (hard stop, chandelier trailing, ATR target) are checked
    intrabar against bar i's high/low and take priority over signal exits
  * one position at a time per (strategy, coin) run; flat between trades

Costs: taker fee per side + slippage per side (from RiskConfig), optional
hourly funding accrual from the public fundingHistory endpoint.

Sizing: risk ``risk_frac`` of equity per trade on the hard-stop distance;
notional capped at ``max_leverage`` x equity.

Paper only. Nothing here touches live execution.
"""

from __future__ import annotations

import math
import time
import urllib.request
import json

import numpy as np
import pandas as pd

from .base import RiskConfig, atr

INFO_URL = "https://api.hyperliquid.xyz/info"
BARS_PER_YEAR = {"1m": 525_600, "5m": 105_120, "15m": 35_040, "1h": 8_760, "4h": 2_190, "1d": 365}


def _fetch_funding(coin: str, start_ms: int, end_ms: int) -> list[float]:
    """Hourly funding rates for a coin window. Returns [] on any failure."""
    try:
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_ms,
            "endTime": end_ms,
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            INFO_URL, data=data, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode())
        return [float(r["fundingRate"]) for r in rows if "fundingRate" in r]
    except Exception:
        return []


def funding_pnl_usd(side: str, notional_usd: float, rates: list[float]) -> float:
    """Signed funding PnL. Positive rate => longs pay shorts."""
    total = sum(rates)
    return -total * notional_usd if side == "long" else total * notional_usd


class BacktestResult:
    def __init__(self, trades: pd.DataFrame, equity: pd.Series, meta: dict):
        self.trades = trades
        self.equity = equity
        self.meta = meta

    def metrics(self) -> dict:
        tr = self.trades
        eq = self.equity
        n = len(tr)
        wins = tr[tr["net_pnl"] > 0] if n else tr
        gross_win = wins["net_pnl"].sum() if n else 0.0
        gross_loss = -tr[tr["net_pnl"] <= 0]["net_pnl"].sum() if n else 0.0
        ret = eq_ret = (eq.iloc[-1] / eq.iloc[0] - 1) if len(eq) > 1 else 0.0
        rets = eq.pct_change().fillna(0)
        bpy = self.meta.get("bars_per_year", 8760)
        sharpe = (
            float(rets.mean() / rets.std() * math.sqrt(bpy)) if rets.std() > 0 else 0.0
        )
        roll_max = eq.cummax()
        dd = (eq - roll_max) / roll_max
        return {
            "trades": n,
            "win_rate": float(len(wins) / n) if n else 0.0,
            "net_return_pct": float(ret * 100),
            "sharpe": sharpe,
            "max_dd_pct": float(dd.min() * 100),
            "expectancy_usd": float(tr["net_pnl"].mean()) if n else 0.0,
            "profit_factor": float(gross_win / gross_loss) if gross_loss > 0 else float("inf") if gross_win > 0 else 0.0,
            "total_fees_usd": float(tr["fees_usd"].sum()) if n else 0.0,
            "total_funding_usd": float(tr["funding_usd"].sum()) if n else 0.0,
            "net_pnl_usd": float(tr["net_pnl"].sum()) if n else 0.0,
        }


def run_backtest(
    df: pd.DataFrame,
    risk: RiskConfig,
    coin: str = "BTC",
    interval: str = "1h",
    start_equity: float = 10_000.0,
    warmup: int = 0,
    use_funding: bool = True,
) -> BacktestResult:
    """Run one strategy/coin backtest. ``df`` must already carry signal columns."""
    o = df["o"].to_numpy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    t = df["t"].to_numpy()
    n = len(df)

    le = df.get("long_entry", pd.Series(False, index=df.index)).fillna(False).to_numpy()
    se = df.get("short_entry", pd.Series(False, index=df.index)).fillna(False).to_numpy()
    lx = df.get("long_exit", pd.Series(False, index=df.index)).fillna(False).to_numpy()
    sx = df.get("short_exit", pd.Series(False, index=df.index)).fillna(False).to_numpy()

    a = atr(df["h"], df["l"], df["c"], risk.atr_window).to_numpy()

    equity = start_equity
    eq_curve = np.full(n, np.nan)
    pos = None  # dict with side, qty, entry, stop, trail_mult, target, entry_bar, atr_v, peak
    trades: list[dict] = []
    funding_cache: dict[str, list[float]] = {}

    def funding_for(entry_ms: int, exit_ms: int) -> list[float]:
        key = f"{entry_ms//3_600_000}-{(exit_ms or entry_ms)//3_600_000}"
        if key not in funding_cache:
            funding_cache[key] = _fetch_funding(coin, entry_ms, exit_ms or entry_ms + 3_600_000)
            time.sleep(0.1)
        return funding_cache[key]

    for i in range(n):
        # 1) risk exits intrabar
        if pos is not None:
            side = pos["side"]
            exit_px = None
            reason = None
            if side == "long":
                # hard stop
                if l[i] <= pos["stop"]:
                    exit_px = min(pos["stop"], o[i])
                    reason = "stop"
                elif pos["target"] is not None and h[i] >= pos["target"]:
                    exit_px = max(pos["target"], o[i])
                    reason = "target"
                else:
                    # chandelier trailing
                    if risk.trail_atr_mult:
                        pos["peak"] = max(pos["peak"], h[i])
                        trail = pos["peak"] - risk.trail_atr_mult * pos["atr_v"]
                        pos["stop"] = max(pos["stop"], trail)
            else:
                if h[i] >= pos["stop"]:
                    exit_px = max(pos["stop"], o[i])
                    reason = "stop"
                elif pos["target"] is not None and l[i] <= pos["target"]:
                    exit_px = min(pos["target"], o[i])
                    reason = "target"
                else:
                    if risk.trail_atr_mult:
                        pos["peak"] = min(pos["peak"], l[i])
                        trail = pos["peak"] + risk.trail_atr_mult * pos["atr_v"]
                        pos["stop"] = min(pos["stop"], trail)
            # max hold
            if exit_px is None and risk.max_hold_bars and i - pos["entry_bar"] >= risk.max_hold_bars:
                exit_px = o[i]
                reason = "max_hold"
            # strategy exit signal from previous bar
            if exit_px is None and i > 0:
                if (side == "long" and lx[i - 1]) or (side == "short" and sx[i - 1]):
                    exit_px = o[i]
                    reason = "signal"
            if exit_px is not None:
                qty = pos["qty"]
                gross = (exit_px - pos["entry"]) * qty if side == "long" else (pos["entry"] - exit_px) * qty
                notional = pos["entry"] * qty
                fees = (risk.fee_rate + risk.slippage_rate) * (notional + exit_px * qty)
                fund = 0.0
                if use_funding:
                    rates = funding_for(int(t[pos["entry_bar"]]), int(t[i]))
                    fund = funding_pnl_usd(side, notional, rates)
                net = gross - fees + fund
                equity += net
                trades.append(
                    {
                        "entry_t": int(t[pos["entry_bar"]]),
                        "exit_t": int(t[i]),
                        "side": side,
                        "entry_px": pos["entry"],
                        "exit_px": exit_px,
                        "qty": qty,
                        "gross_pnl": gross,
                        "fees_usd": fees,
                        "funding_usd": fund,
                        "net_pnl": net,
                        "exit_reason": reason,
                    }
                )
                pos = None

        # 2) entries on previous-bar signal
        if pos is None and i > 0 and i >= warmup:
            sig_long = bool(le[i - 1]) and risk.allow_longs
            sig_short = bool(se[i - 1]) and risk.allow_shorts
            if sig_long or sig_short:
                side = "long" if sig_long else "short"
                entry = o[i]
                atr_v = a[i - 1]
                if atr_v and atr_v > 0 and np.isfinite(atr_v):
                    stop_dist = risk.stop_atr_mult * atr_v
                    risk_usd = equity * risk.risk_frac
                    notional = min(risk_usd / (stop_dist / entry), equity * risk.max_leverage)
                    qty = notional / entry
                    if qty > 0:
                        stop = entry - stop_dist if side == "long" else entry + stop_dist
                        target = None
                        if risk.target_atr_mult:
                            target = (
                                entry + risk.target_atr_mult * atr_v
                                if side == "long"
                                else entry - risk.target_atr_mult * atr_v
                            )
                        pos = {
                            "side": side,
                            "qty": qty,
                            "entry": entry,
                            "stop": stop,
                            "target": target,
                            "entry_bar": i,
                            "atr_v": atr_v,
                            "peak": h[i] if side == "long" else l[i],
                        }

        # 3) mark equity at close
        mtm = equity
        if pos is not None:
            q = pos["qty"]
            mtm = equity + ((c[i] - pos["entry"]) * q if pos["side"] == "long" else (pos["entry"] - c[i]) * q)
        eq_curve[i] = mtm

    eq_s = pd.Series(eq_curve, index=df.index).ffill().fillna(start_equity)
    trades_df = pd.DataFrame(trades)
    meta = {
        "coin": coin,
        "interval": interval,
        "bars": n,
        "bars_per_year": BARS_PER_YEAR.get(interval, 8760),
        "start_equity": start_equity,
        "end_equity": float(eq_s.iloc[-1]),
    }
    return BacktestResult(trades_df, eq_s, meta)
