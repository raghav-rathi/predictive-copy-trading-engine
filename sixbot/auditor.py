"""BOT 6 - AUDITOR.

Journals every trade (entry, exit, fee, slippage each on its own line, result
in R) plus every SKIPPED alert, then grades the desk against the locked
go/no-go thresholds from DESK_RULES.md:

    trades >= GO_NOGO_TRADES_MIN   | win rate >= GO_NOGO_WIN_RATE_MIN
    expectancy >= GO_NOGO_EXPECTANCY_MIN_R | max drawdown <= GO_NOGO_MAX_DD_MAX

Thresholds were locked BEFORE the backtest. Never tuned after seeing results.
"""
import csv
import json

from .config import get


class Auditor:
    def __init__(self):
        self.trades = []    # one dict per closed position
        self.skipped = []   # one dict per skipped / unfilled alert

    # -- journaling -----------------------------------------------------
    def journal_trade(self, coin, alert_id, prime, entry_ms, entry, qty,
                      notional, risked, adds, exit_ms, exit_price,
                      exit_reason, fee_entry, fee_exit,
                      slip_entry, slip_exit, skip_flag=""):
        gross = (entry - exit_price) * qty            # short PnL
        fees = fee_entry + fee_exit
        slip = slip_entry + slip_exit
        net = gross - fees - slip
        r = net / risked if risked else 0.0
        self.trades.append({
            "coin": coin, "alert_id": alert_id, "prime": prime,
            "skip_flag": skip_flag,
            "entry_ms": entry_ms, "entry": entry,
            "exit_ms": exit_ms, "exit": exit_price, "exit_reason": exit_reason,
            "qty": qty, "notional": notional, "risked": risked, "adds": adds,
            "fee_entry": fee_entry, "fee_exit": fee_exit,
            "slip_entry": slip_entry, "slip_exit": slip_exit,
            "gross_pnl": gross, "fees": fees, "slippage": slip,
            "net_pnl": net, "r": r,
            "win": net > 0,
        })

    def journal_skip(self, coin, alert_id, asof_ms, reason, prime, note=""):
        self.skipped.append({
            "coin": coin, "alert_id": alert_id, "asof_ms": asof_ms,
            "reason": reason, "prime": prime, "note": note,
        })

    # -- grading --------------------------------------------------------
    def grade(self, equity_start, daily_equity=None):
        t = self.trades
        n = len(t)
        wins = sum(1 for x in t if x["win"])
        win_rate = wins / n if n else 0.0
        expectancy = sum(x["r"] for x in t) / n if n else 0.0
        max_dd = self._max_drawdown(equity_start, daily_equity, t)
        checks = [
            ("trades >= %d" % get("GO_NOGO_TRADES_MIN"),
             n >= get("GO_NOGO_TRADES_MIN"), n),
            ("win rate >= %.0f%%" % (get("GO_NOGO_WIN_RATE_MIN") * 100),
             win_rate >= get("GO_NOGO_WIN_RATE_MIN"), round(win_rate, 4)),
            ("expectancy >= %+.2fR" % get("GO_NOGO_EXPECTANCY_MIN_R"),
             expectancy >= get("GO_NOGO_EXPECTANCY_MIN_R"),
             round(expectancy, 4)),
            ("max drawdown <= %.0f%%" % (get("GO_NOGO_MAX_DD_MAX") * 100),
             max_dd <= get("GO_NOGO_MAX_DD_MAX"), round(max_dd, 4)),
        ]
        return {
            "trades": n, "wins": wins, "win_rate": win_rate,
            "expectancy_r": expectancy, "max_drawdown": max_dd,
            "total_net_pnl": sum(x["net_pnl"] for x in t),
            "total_r": sum(x["r"] for x in t),
            "checks": [{"rule": rule, "pass": ok, "value": val}
                       for rule, ok, val in checks],
            "verdict": "GO" if all(ok for _, ok, _ in checks) else "NO-GO",
        }

    @staticmethod
    def _max_drawdown(equity_start, daily_equity, trades):
        if daily_equity:
            peak, dd = equity_start, 0.0
            for eq in daily_equity:
                peak = max(peak, eq)
                if peak > 0:
                    dd = max(dd, (peak - eq) / peak)
            return dd
        # fallback: closed-trade equity curve in exit order
        eq, peak, dd = equity_start, equity_start, 0.0
        for x in sorted(trades, key=lambda x: x["exit_ms"]):
            eq += x["net_pnl"]
            peak = max(peak, eq)
            dd = max(dd, (peak - eq) / peak if peak > 0 else 0.0)
        return dd

    # -- persistence ----------------------------------------------------
    def save(self, path_prefix):
        with open(path_prefix + "_trades.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["coin", "alert_id", "prime", "skip_flag",
                        "entry_time", "entry",
                        "exit_time", "exit", "exit_reason",
                        "qty", "notional_usd", "risked_usd", "adds",
                        "fee_entry", "fee_exit",
                        "slippage_entry", "slippage_exit",
                        "gross_pnl", "fees_total", "slippage_total",
                        "net_pnl", "r_multiple", "win"])
            for x in self.trades:
                w.writerow([x["coin"], x["alert_id"], x["prime"],
                            x["skip_flag"],
                            x["entry_ms"], round(x["entry"], 6),
                            x["exit_ms"], round(x["exit"], 6),
                            x["exit_reason"], round(x["qty"], 6),
                            round(x["notional"], 2), round(x["risked"], 2),
                            x["adds"], round(x["fee_entry"], 4),
                            round(x["fee_exit"], 4),
                            round(x["slip_entry"], 4),
                            round(x["slip_exit"], 4),
                            round(x["gross_pnl"], 2), round(x["fees"], 4),
                            round(x["slippage"], 4),
                            round(x["net_pnl"], 2), round(x["r"], 4),
                            x["win"]])
        with open(path_prefix + "_skipped.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["coin", "alert_id", "asof_ms", "reason",
                        "prime", "note"])
            for s in self.skipped:
                w.writerow([s["coin"], s["alert_id"], s["asof_ms"],
                            s["reason"], s["prime"], s["note"]])
