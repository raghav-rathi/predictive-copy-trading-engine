#!/usr/bin/env python3
"""Empirical check: what would funding payments have done to the live
paper test's track record?

Read-only. The live paper test's CSV (~/workspace/copy-trading/
paper_trades.csv) is a fill log, so closed trades are reconstructed
by FIFO-matching open/close fills per (target, coin, side). For each
closed leg we accrue hourly funding from real Hyperliquid
`fundingHistory` (long pays when funding positive, short earns) and
compare the tracker's modeled fee (0.035% taker assumption) against
the verified real base tier (0.045% taker via `userFees`).

Usage: python3 scripts/funding_impact.py
"""
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                "..", "hyperliquid"))
from costs import (  # noqa: E402
    FundingLedger,
    taker_fee_rate,
)

TRACKER_CSV = os.path.expanduser("~/workspace/copy-trading/paper_trades.csv")
INFO_URL = "https://api.hyperliquid.xyz/info"
ASSUMED_TAKER = 0.00035  # the paper test's current fee assumption

CLOSE_ACTIONS = {"maxhold", "stop", "target_exit", "tp", "trailing"}


def read_fills(path: str) -> list[dict]:
    fills = []
    with open(path, newline="") as f:
        body = (ln for ln in f if not ln.lstrip().startswith("#"))
        for r in csv.DictReader(body):
            fills.append(r)
    fills.sort(key=lambda r: float(r["ts"]))
    return fills


def reconstruct(fills: list[dict]) -> list[dict]:
    """FIFO-match opens to closes -> closed legs."""
    lots: dict[tuple, list[dict]] = {}
    closed = []
    for r in fills:
        key = (r["target"], r["coin"], r["side"])
        action = r["action"]
        if action == "open":
            lots.setdefault(key, []).append({
                "ts": float(r["ts"]) / 1000.0,
                "px": float(r["price"]),
                "size": abs(float(r["size"])),
            })
        elif action in CLOSE_ACTIONS:
            need = abs(float(r["size"]))
            close_px = float(r["price"])
            close_ts = float(r["ts"]) / 1000.0
            realized = float(r["realized_pnl_usd"] or 0.0)
            modeled_fee = float(r["fee_usd"] or 0.0)
            queue = lots.get(key, [])
            matched = 0.0
            while need > 1e-12 and queue:
                lot = queue[0]
                take = min(need, lot["size"])
                frac = take / need if need > 0 else 0.0
                closed.append({
                    "target": r["target"], "coin": r["coin"],
                    "side": r["side"], "size": take,
                    "entry_px": lot["px"], "exit_px": close_px,
                    "entry_ts": lot["ts"], "exit_ts": close_ts,
                    "realized_pnl_usd": realized * frac,
                    "modeled_fee_usd": modeled_fee * frac,
                    "reason": r["reason"],
                })
                matched += take
                need -= take
                lot["size"] -= take
                if lot["size"] <= 1e-12:
                    queue.pop(0)
            # unmatched remainder: target-side close with no recorded
            # open lot (startup sync); attribute funding on close size
            # from close time only -> skip (conservative: no data).
    return closed


def main() -> int:
    legs = reconstruct(read_fills(TRACKER_CSV))
    if not legs:
        print("no closed legs reconstructed")
        return 1

    funding = FundingLedger(INFO_URL)
    real_taker, fee_src = taker_fee_rate(INFO_URL)

    tot_realized = tot_fund = tot_fee_delta = 0.0
    per_side: dict[str, list] = {}
    per_coin: dict[str, list] = {}
    n_funded = 0

    for leg in legs:
        fund = funding.accrue(leg["coin"], leg["side"],
                              leg["size"] * leg["entry_px"],
                              leg["entry_ts"], leg["exit_ts"])
        fee_delta = (real_taker - ASSUMED_TAKER) * leg["size"] * (
            leg["entry_px"] + leg["exit_px"])
        tot_realized += leg["realized_pnl_usd"]
        tot_fund += fund
        tot_fee_delta += fee_delta
        if abs(fund) > 1e-12:
            n_funded += 1
        for name, d in (("side", per_side), ("coin", per_coin)):
            b = d.setdefault(leg[name], [0.0, 0.0, 0])
            b[0] += leg["realized_pnl_usd"]
            b[1] += fund
            b[2] += 1

    n = len(legs)
    print(f"closed legs reconstructed: {n} ({n_funded} with nonzero funding)")
    print(f"fee: tracker assumes 0.035% | real base tier {real_taker:.5%} "
          f"({fee_src})")
    print()
    print(f"{'metric':34s} {'total USD':>12s} {'per leg':>12s}")
    print("-" * 60)
    print(f"{'realized PnL (tracker, net of modeled fees)':34s} "
          f"{tot_realized:12.2f} {tot_realized / n:12.4f}")
    print(f"{'funding PnL (real history, signed)':34s} "
          f"{tot_fund:+12.2f} {tot_fund / n:+12.4f}")
    print(f"{'extra fees at real tier vs assumed':34s} "
          f"{-tot_fee_delta:+12.2f} {-tot_fee_delta / n:+12.4f}")
    honest = tot_realized + tot_fund - tot_fee_delta
    print(f"{'honest total':34s} {honest:12.2f}")
    print()
    print("per side (realized / funding / n):")
    for side, (pp, fp, c) in sorted(per_side.items()):
        print(f"  {side:6s} {pp:+10.2f} / {fp:+10.2f} / {c}")
    print("per coin (realized / funding / n):")
    for coin, (pp, fp, c) in sorted(per_coin.items(),
                                    key=lambda kv: -abs(kv[1][1]))[:12]:
        print(f"  {coin:8s} {pp:+10.2f} / {fp:+10.2f} / {c}")
    if funding.gaps:
        print(f"\nnote: {len(funding.gaps)} funding-history gap(s) "
              f"accrued as 0.0")
    start = min(leg["entry_ts"] for leg in legs)
    end = max(leg["exit_ts"] for leg in legs)
    days = (end - start) / 86400
    print(f"window: {datetime.fromtimestamp(start, timezone.utc):%Y-%m-%d} "
          f"-> {datetime.fromtimestamp(end, timezone.utc):%Y-%m-%d} "
          f"({days:.1f}d)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
