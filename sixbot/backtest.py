#!/usr/bin/env python3
"""Paper backtest of the six-bot desk (short-only USDT perps).

Pipeline per coin, walked on closed 1H candles (finest grain):
  daily close -> SCREENER (flip?) -> CARTOGRAPHER (FVG ladder)
               -> RISK OFFICER (size) -> GATE (alert / skip flags)
  1H          -> 1H touch + rejection = confirmation -> entry at NEXT 1H open
               -> EXIT CLERK: 4H intrabar stop at zone top, daily close above
                  anchor -> exit, 72h stale, 1R -> move stop to breakeven
                  (unlocks adds: 0.5% risk on 1H re-touch confirmations)
  end         -> AUDITOR journals everything, grades vs locked thresholds.

Conservative assumptions (see sixbot/DESK_RULES.md + README.md):
  - 0.05% taker fee per side, 0.02% slippage per side (price worsened).
  - Entries at the next 1H open after the confirming 1H close.
  - Stop = zone top, no buffer; stop fills assume the stop price unless the
    candle gapped through it (then the open).
  - Main ledger AUTO-TAKES every alert the gate emits, including ones flagged
    SKIP (e.g. TESTED_ZONE); the auditor reports the clean-vs-skipped split
    so we see "what SKIPPED would have done".

Usage: python3 backtest.py [--coins BTC,ETH] [--out results_dir]
"""
import csv
import datetime
import json
import os
import sys

# repo root on sys.path so `sixbot` imports as a package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sixbot import config, screener, cartographer, risk_officer, gate, exit_clerk, auditor  # noqa: E402
from sixbot.data import load as load_candles, COINS  # noqa: E402

DAY = 86400_000
H4 = 4 * 3600_000
H1 = 3600_000
P = config.PARAMS
FEE = P["FEE_PCT_PER_SIDE"] / 100.0
SLIP = P["SLIPPAGE_PCT_PER_SIDE"] / 100.0


def _dt(ms):
    return datetime.datetime.fromtimestamp(ms / 1000,
                                          tz=datetime.timezone.utc).strftime("%Y-%m-%d")


class Desk:
    """One paper account running the desk across all coins."""

    def __init__(self):
        self.equity = P["ACCOUNT_EQUITY_USD"]
        self.start_equity = self.equity
        self.aud = auditor.Auditor()
        self.bull_flips = 0
        self.flips = 0

    # -- fills ------------------------------------------------------
    def open_position(self, coin, alert, fill_raw, fill_ms):
        entry = fill_raw * (1 - SLIP)  # short: worse fill = lower
        size = risk_officer.size_initial(self.equity, entry, alert.stop)
        if size is None:
            self.aud.journal_skip(coin, alert.alert_id, alert.asof_ms,
                                  "INVALID_SIZE", alert.prime)
            return None
        pos = risk_officer.Position(
            coin=coin, entry=entry, avg_entry=entry, stop=alert.stop,
            zone_top=alert.zone_top, zone_bottom=alert.zone_bottom,
            anchor_high=alert.anchor_high, qty=size.qty,
            risk_dist=alert.stop - entry, risked=size.risk_amount,
            alert_id=alert.alert_id, prime=alert.prime,
            skip_flag=alert.skip_reason,
            fee_entry=size.notional * FEE, slip_entry=size.notional * SLIP,
            entry_ms=fill_ms)
        return pos

    def add_to_position(self, pos, fill_raw):
        add_entry = fill_raw * (1 - SLIP)
        size = risk_officer.size_add(self.equity, add_entry, pos.entry)
        if size is None or not risk_officer.add_approved(pos):
            return False
        pos.avg_entry = ((pos.qty * pos.avg_entry + size.qty * add_entry)
                         / (pos.qty + size.qty))
        pos.qty += size.qty
        pos.risked += size.risk_amount
        pos.fee_entry += size.notional * FEE
        pos.slip_entry += size.notional * SLIP
        pos.adds += 1
        return True

    def close_position(self, pos, exit_ms, exit_raw, reason, gap_open=None):
        # gap through the stop -> filled at the open (worse for a short)
        px = max(exit_raw, gap_open) if gap_open else exit_raw
        exit_px = px * (1 + SLIP)  # short exit = buy: worse = higher
        fee_exit = pos.qty * exit_px * FEE
        slip_exit = pos.qty * exit_px * SLIP
        before = self.equity
        self.aud.journal_trade(
            pos.coin, pos.alert_id, pos.prime, pos.entry_ms, pos.avg_entry,
            pos.qty, pos.qty * pos.avg_entry, pos.risked, pos.adds,
            exit_ms, exit_px, reason,
            pos.fee_entry, fee_exit, pos.slip_entry, slip_exit,
            skip_flag=pos.skip_flag)
        net = self.aud.trades[-1]["net_pnl"]
        self.equity = before + net
        return net


def run_coin(coin, d, h4, h1, desk):
    d, h4, h1 = d[:-1], h4[:-1], h1[:-1]  # drop partial live candles
    aud = desk.aud
    pending = None            # Alert awaiting 1H confirmation
    entry_order = None        # (Alert) confirmed -> fill at next 1H open
    add_order = False         # confirmed re-touch -> add at next 1H open
    pos = None
    mfe_r = 0.0
    di, h4i = 2, 0

    for j, c in enumerate(h1):
        tc = c["t"] + H1

        # ---- daily closes: screener + exit clerk (anchor) ----
        while di < len(d) and d[di]["t"] + DAY <= tc:
            dc, dclose_t = d[di], d[di]["t"] + DAY
            h4c = [x for x in h4 if x["t"] + H4 <= dclose_t]
            ev = screener.scan(d[:di + 1], h4c, coin)
            if ev is not None and ev.direction == "bull":
                desk.bull_flips += 1
            elif ev is not None:
                desk.flips += 1
                ladder = cartographer.build_ladder(coin, d[:di + 1], h4c,
                                                   dclose_t)
                alert, skip = gate.evaluate(coin, ladder, dclose_t)
                if alert is None:
                    aud.journal_skip(coin, f"{coin}-{dclose_t}", dclose_t,
                                     skip, ev.prime)
                else:
                    alert.prime = ev.prime
                    if skip:  # flagged SKIP but auto-taken in the main ledger
                        aud.journal_skip(
                            coin, alert.alert_id, dclose_t, skip, ev.prime,
                            note="auto-taken in main ledger; see auditor split")
                    if pos is not None:
                        aud.journal_skip(coin, alert.alert_id, dclose_t,
                                         "POSITION_ALREADY_OPEN", ev.prime)
                    else:
                        if pending is not None:
                            aud.journal_skip(coin, pending.alert_id,
                                             pending.asof_ms, "SUPERSEDED",
                                             pending.prime)
                        pending = alert
            if pos is not None:
                sig = exit_clerk.check_daily(pos, dc, pos.anchor_high)
                if sig.action == "EXIT":
                    desk.close_position(pos, dclose_t, sig.price, sig.reason,
                                        gap_open=dc["o"])
                    pos = None
                    add_order = False
                    mfe_r = 0.0
            di += 1

        # ---- 4H closes: stale check ----
        while h4i < len(h4) and h4[h4i]["t"] + H4 <= tc:
            hc, hclose_t = h4[h4i], h4[h4i]["t"] + H4
            if pos is not None:
                sig = exit_clerk.check_stale(pos, hclose_t, mfe_r)
                if sig.action == "EXIT":
                    desk.close_position(pos, hclose_t, hc["c"], sig.reason)
                    pos = None
                    add_order = False
                    mfe_r = 0.0
            h4i += 1

        # ---- fills at this 1H open ----
        if entry_order is not None:
            pos = desk.open_position(coin, entry_order, c["o"], c["t"])
            if pos is not None:
                mfe_r = 0.0
            entry_order = None
        if add_order and pos is not None:
            desk.add_to_position(pos, c["o"])
            add_order = False

        # ---- pending alert: 1H confirmation ----
        if pending is not None and pos is None and entry_order is None:
            if c["c"] >= pending.zone_top:
                aud.journal_skip(coin, pending.alert_id, pending.asof_ms,
                                 "ZONE_INVALIDATED", pending.prime)
                pending = None
            elif c["h"] >= pending.zone_bottom and c["c"] < pending.zone_top:
                if c["o"] >= pending.zone_top or (j + 1 < len(h1)
                                                 and h1[j + 1]["o"] >= pending.zone_top):
                    aud.journal_skip(coin, pending.alert_id, pending.asof_ms,
                                     "INVALID_ENTRY_GAP", pending.prime)
                    pending = None
                else:
                    entry_order = pending  # fill at next 1H open
                    pending = None
            elif gate.expired(pending, tc):
                aud.journal_skip(coin, pending.alert_id, pending.asof_ms,
                                 "EXPIRED", pending.prime)
                pending = None

        # ---- open position: stops, breakeven, adds ----
        if pos is not None:
            if c["h"] >= pos.stop:
                desk.close_position(pos, tc, pos.stop, "STOP",
                                    gap_open=c["o"])
                pos = None
                add_order = False
                mfe_r = 0.0
            else:
                mfe_r = max(mfe_r, (pos.entry - c["l"]) / pos.risk_dist)
                if exit_clerk.maybe_move_breakeven(pos, mfe_r).action == "MOVE_BE":
                    pos.stop = pos.entry
                    pos.breakeven = True
                # add trigger: 1H re-touch + rejection while at breakeven
                if (pos.breakeven
                        and pos.adds < P["MAX_ADDS_PER_POSITION"]
                        and c["h"] >= pos.zone_bottom
                        and c["c"] < pos.zone_top):
                    add_order = True  # fill at next 1H open

    # ---- data end: close leftovers ----
    if entry_order is not None:
        aud.journal_skip(coin, entry_order.alert_id, entry_order.asof_ms,
                         "EXPIRED", entry_order.prime, note="data end")
        entry_order = None
    if pos is not None:
        desk.close_position(pos, h1[-1]["t"] + H1, h1[-1]["c"], "DATA_END")
    if pending is not None:
        aud.journal_skip(coin, pending.alert_id, pending.asof_ms,
                         "EXPIRED", pending.prime, note="data end")


def daily_mtm_equity(desk, coins_data):
    """Daily mark-to-market equity curve across all coins."""
    start = min(d[0]["t"] for d, _, _ in coins_data.values())
    end = max(d[-2]["t"] for d, _, _ in coins_data.values())
    closes = {}
    for coin, (d, _, _) in coins_data.items():
        closes[coin] = {x["t"]: x["c"] for x in d}
    days = []
    t = (start // DAY) * DAY
    while t <= end:
        days.append(t)
        t += DAY
    curve = []
    for day in days:
        day_end = day + DAY
        eq = desk.start_equity
        for x in desk.aud.trades:
            if x["exit_ms"] <= day_end:
                eq += x["net_pnl"]
            elif x["entry_ms"] <= day_end:
                px = closes[x["coin"]].get(day)
                if px:
                    eq += (x["entry"] - px) * x["qty"]
        curve.append(eq)
    return curve


def main():
    coins = COINS
    if "--coins" in sys.argv:
        coins = sys.argv[sys.argv.index("--coins") + 1].split(",")
    out = "results"
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)

    desk = Desk()
    coins_data = {}
    for coin in coins:
        d = load_candles(coin, "1d")
        h4 = load_candles(coin, "4h")
        h1 = load_candles(coin, "1h")
        coins_data[coin] = (d, h4, h1)
        print(f"{coin}: {len(d)}d / {len(h4)}x4h / {len(h1)}x1h", flush=True)

    for coin in coins:
        d, h4, h1 = coins_data[coin]
        run_coin(coin, d, h4, h1, desk)
        print(f"  {coin} done: equity={desk.equity:,.2f} "
              f"trades={len(desk.aud.trades)}", flush=True)

    curve = daily_mtm_equity(desk, coins_data)
    grade = desk.aud.grade(desk.start_equity, curve)

    # clean-vs-skipped split ("what SKIPPED would have done")
    for subset, name in (([x for x in desk.aud.trades if not x["skip_flag"]], "clean"),
                         ([x for x in desk.aud.trades if x["skip_flag"]], "skipped_flagged")):
        n = len(subset)
        wr = sum(1 for x in subset if x["win"]) / n if n else 0
        ex = sum(x["r"] for x in subset) / n if n else 0
        print(f"  split {name}: n={n} win_rate={wr:.2%} expectancy={ex:+.3f}R "
              f"net={sum(x['net_pnl'] for x in subset):+.2f}")

    prefix = os.path.join(out, "sixbot")
    desk.aud.save(prefix)
    with open(prefix + "_grade.json", "w") as fh:
        json.dump(grade, fh, indent=2)
    with open(prefix + "_equity.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["day", "equity"])
        start = min(d[0]["t"] for d, _, _ in coins_data.values())
        t = (start // DAY) * DAY
        for eq in curve:
            w.writerow([_dt(t), round(eq, 2)])
            t += DAY

    print("\n================ AUDITOR VERDICT ================")
    print(f"trades: {grade['trades']}  wins: {grade['wins']}  "
          f"win_rate: {grade['win_rate']:.2%}  "
          f"expectancy: {grade['expectancy_r']:+.4f}R")
    print(f"max_drawdown: {grade['max_drawdown']:.2%}  "
          f"net_pnl: {grade['total_net_pnl']:+.2f} USD  "
          f"total_R: {grade['total_r']:+.2f}R")
    print(f"bear flips: {desk.flips}  bull flips (context): {desk.bull_flips}  "
          f"skipped alerts: {len(desk.aud.skipped)}")
    for chk in grade["checks"]:
        print(f"  [{'PASS' if chk['pass'] else 'FAIL'}] {chk['rule']} "
              f"(actual: {chk['value']})")
    print(f"VERDICT: {grade['verdict']}")
    print("=================================================")


if __name__ == "__main__":
    main()
