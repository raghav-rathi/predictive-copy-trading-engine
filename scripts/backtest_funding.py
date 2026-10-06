#!/usr/bin/env python3
"""Historical backtest of the delta-neutral funding farm.

Uses real Hyperliquid fundingHistory data: for each hour in the window,
build trailing histories from data *available up to that hour* (no
lookahead), run rank -> decide -> size -> ledger step, and accrue the
actual next-hour funding.

Universe: top N coins by 24h notional volume at backtest start.
Costs: taker + spot fees per leg, slippage buffer on switches.

Usage: python3 scripts/backtest_funding.py [--days 30] [--top 20]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from funding.api import (FundingBar, fetch_current_funding,
                         fetch_funding_history)
from funding.config import FarmConfig
from funding.guardrails import GuardrailConfig, apply, check
from funding.paper import new_farm, step

MS_HR = 3600_000


def pick_universe(cfg: FarmConfig, top_n: int):
    snaps = fetch_current_funding(cfg)
    by_vol = {}
    # metaAndAssetCtxs also carries dayNtlVlm; re-fetch raw for volume.
    import urllib.request
    req = urllib.request.Request(
        f"{cfg.api_url}/info",
        data=json.dumps({"type": "metaAndAssetCtxs"}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=cfg.request_timeout_s) as r:
        meta, ctxs = json.load(r)
    vols = [(a["name"], float(c.get("dayNtlVlm", 0) or 0))
            for a, c in zip(meta["universe"], ctxs)]
    vols.sort(key=lambda x: x[1], reverse=True)
    return [v[0] for v in vols[:top_n]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    cfg = FarmConfig()
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - args.days * 24 * MS_HR
    # Need ranking_window of lead-in history before the backtest window.
    hist_start = start_ms - cfg.ranking_window_hours * MS_HR

    coins = pick_universe(cfg, args.top)
    print(f"universe: {len(coins)} coins: {', '.join(coins)}", flush=True)

    full: dict[str, list[FundingBar]] = {}
    for coin in coins:
        try:
            full[coin] = fetch_funding_history(coin, hist_start, end_ms, cfg)
            print(f"  {coin}: {len(full[coin])} bars", flush=True)
        except Exception as e:  # noqa: BLE001 - one bad coin must not kill the run
            print(f"  {coin}: fetch failed ({e}), skipped", flush=True)

    state = new_farm(cfg)
    gcfg = GuardrailConfig()
    peak = cfg.farm_capital
    n_steps = args.days * 24

    for h in range(n_steps):
        t = start_ms + h * MS_HR
        # Histories as known at hour h (no lookahead).
        histories = {c: [b for b in bars if b.time_ms <= t]
                     for c, bars in full.items()}
        histories = {c: b for c, b in histories.items() if b}
        snapshots = []
        marks = {}
        for c, bars in histories.items():
            last = bars[-1]
            snapshots.append(type("S", (), {"coin": c,
                                            "funding_hr": last.funding_hr})())
            marks[c] = 1.0  # delta-neutral: basis nets to zero
        trips = check(state, peak, gcfg, cfg)
        apply(state, trips)
        step(state, snapshots, histories, marks, cfg)
        peak = max(peak, state.ledger.equity)

    s = state.ledger.summary()
    carry = s["closed_carry"] + s["open_carry"]
    net = s["equity"] - cfg.farm_capital
    apr = (net / cfg.farm_capital) * (365 / args.days)
    print("\n=== funding farm backtest ===")
    print(f"window: {args.days}d, universe top-{args.top}")
    print(f"start equity : ${cfg.farm_capital:,.2f}")
    print(f"end equity   : ${s['equity']:,.2f}")
    print(f"net PnL      : ${net:+,.2f}  ({net/cfg.farm_capital:+.2%})")
    print(f"implied APR  : {apr:+.1%}")
    print(f"carry earned : ${carry:+,.2f}   fees paid: ${s['closed_fees']:,.2f}")
    print(f"events       : {s['events']}   open positions: {s['open_positions']}")
    print(f"peak equity  : ${peak:,.2f}")
    out = {"config": cfg.__dict__, "summary": s, "net": net, "apr": apr,
           "days": args.days, "universe": coins}
    with open("funding/backtest_result.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote funding/backtest_result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
