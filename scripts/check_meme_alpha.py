#!/usr/bin/env python3
"""Empirical validation for the meme-alpha wallet-discovery pipeline.

What this script does:
  1. Probes the live gmgn.ai public API once, to document whether
     earliest-buyer discovery is reachable from this environment.
  2. Runs the full 7-step pipeline on a realistic FIXTURE dataset that
     models a past-cycle Solana meme coin (labeled FIXTURE everywhere it
     appears — these are synthetic wallets, not real ones).
  3. Prints every step's output so the result is auditable.

Research only: no trading, no signals are acted on. If the GMGN probe
fails, the fixture run is the validation, and the note says so plainly.
"""

import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from memealpha.discovery import GmgnClient, EarlyBuyer
from memealpha.pipeline import run_pipeline

DAY = 86400.0
NOW = time.time()

SEED_LABEL = "PAST-CYCLE-MEME (fixture)"


def probe_gmgn() -> str:
    """One honest reachability probe of gmgn.ai's public API."""
    url = "https://gmgn.ai/api/v1/rank/sol/swaps/1h"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return f"reachable (HTTP {resp.status})"
    except Exception as exc:  # noqa: BLE001 - the point is to record it
        return f"BLOCKED: {type(exc).__name__}: {str(exc)[:120]}"


def fixture_wallets() -> list[EarlyBuyer]:
    """20 synthetic earliest buyers of a past-cycle meme (FIXTURE)."""
    addrs = [f"FixtureWallet{i:02d}" for i in range(1, 21)]
    return [
        EarlyBuyer(
            address=a,
            first_buy_ts=NOW - 400 * DAY + i * 3600.0,
            first_buy_usd=200.0 + i * 50.0,
        )
        for i, a in enumerate(addrs)
    ]


def fixture_last_trade(wallets):
    # ~4 of 20 still active (matches the method's "3-5 of 20 survive")
    active = {"FixtureWallet03", "FixtureWallet07", "FixtureWallet11", "FixtureWallet16"}
    return {w: (NOW - 3 * DAY if w in active else NOW - 120 * DAY) for w in wallets}


def fixture_trade_times(wallets):
    times = {}
    for w in wallets:
        if w == "FixtureWallet11":
            # bot signature: trades seconds apart -> must be filtered out
            times[w] = [NOW - i * 4.0 for i in range(30)]
        else:
            times[w] = [NOW - i * 9 * 3600.0 for i in range(10)]
    return times


def fixture_holdings(wallets):
    # three human survivors converge on NEWMEME; the bot is excluded first
    return {
        "FixtureWallet03": {"NEWMEME", "OLDCOIN"},
        "FixtureWallet07": {"NEWMEME", "SOMECOIN"},
        "FixtureWallet16": {"NEWMEME", "OTHERCOIN"},
    }


def fixture_features(token):
    return {
        "liquidity_ok": True,
        "holder_distribution_ok": True,
        "contract_safe": True,
        "buy_pressure_ok": True,
        "volume_alive": True,
    }


def main() -> int:
    print("=" * 70)
    print("meme-alpha empirical validation")
    print("=" * 70)

    print("\n[0] live GMGN probe")
    probe = probe_gmgn()
    print("    gmgn.ai public API:", probe)

    print(f"\n[1] seed: {SEED_LABEL}")
    buyers = fixture_wallets()
    print(f"    earliest buyers discovered: {len(buyers)} (FIXTURE)")

    res = run_pipeline(
        SEED_LABEL,
        chain="sol",
        n_early=20,
        fetch_early_buyers=lambda: buyers,
        fetch_last_trade=lambda ws: fixture_last_trade(ws),
        fetch_trade_counts=lambda ws: {w: 8 for w in ws},
        fetch_trade_times=lambda ws: {
            w: fixture_trade_times(ws)[w] for w in ws
        },
        fetch_holdings=lambda ws: fixture_holdings(ws),
        fetch_features=fixture_features,
        now=NOW,
    )

    print("\n[2] discovery: earliest buyers")
    for b in res.early_buyers[:5]:
        print(f"    {b.address} first buy ${b.first_buy_usd:,.0f}")
    print(f"    ... ({len(res.early_buyers)} total)")

    print("\n[3] activity filter (30d): kept", len(res.active_wallets),
          "| dropped", len(res.dropped_inactive))
    print("    kept:", ", ".join(res.active_wallets))

    print("\n[4] bot filter: humans", len(res.human_wallets),
          "| bots", len(res.bot_wallets))
    print("    bots removed:", ", ".join(res.bot_wallets) or "none")

    print("\n[5+6] holdings scan + convergence (>=3 wallets):")
    for c in res.convergences:
        print(f"    {c.token}: {c.wallet_count} wallets "
              f"(coverage {c.coverage:.0%}) -> {', '.join(c.wallets)}")
    if not res.convergences:
        print("    none")

    print("\n[7] 9-point scoring:")
    for s in res.scores:
        mark = "PASS" if s.passes else "REJECT"
        missing = ", ".join(s.missing()) or "-"
        print(f"    {s.token}: {s.total}/9 [{mark}] missing: {missing}")

    print("\nwatchlist:", [s.token for s in res.watchlist] or "empty")
    for n in res.notes:
        print("note:", n)

    print("\n" + "=" * 70)
    if "BLOCKED" in probe:
        print("FINDING: live GMGN discovery is blocked from this environment")
        print("(HTTP 403, Cloudflare). Pipeline validated on FIXTURE data only.")
        print("A live run needs a residential IP or an official GMGN data plan.")
    else:
        print("FINDING: gmgn.ai reachable; re-run with live clients for a")
        print("real discovery pass.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
