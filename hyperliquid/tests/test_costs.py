#!/usr/bin/env python3
"""Unit tests for hyperliquid/costs.py (funding + fee accounting).

Run:  python3 -m pytest hyperliquid/tests/test_costs.py -q
      (or) python3 hyperliquid/tests/test_costs.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from costs import (  # noqa: E402
    BASE_TAKER_FEE,
    FundingLedger,
    funding_pnl_usd,
    maker_fee_rate,
    round_trip_costs,
    taker_fee_rate,
)

PASSED = FAILED = 0


def check(name, cond, detail=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ok   {name}")
    else:
        FAILED += 1
        print(f"  FAIL {name} {detail}")


def fake_post_factory(fees=None, funding_rows=None, fail=False):
    def post(url, payload):
        if fail:
            raise ConnectionError("boom")
        if payload.get("type") == "userFees":
            return fees
        if payload.get("type") == "fundingHistory":
            return funding_rows or []
        raise AssertionError(f"unexpected payload {payload}")
    return post


# -- funding sign conventions ---------------------------------------------

check("long pays positive funding",
      funding_pnl_usd("long", 1000.0, [0.0001]) == -0.1)

check("short earns positive funding",
      funding_pnl_usd("short", 1000.0, [0.0001]) == 0.1)

check("negative funding flips: long earns",
      funding_pnl_usd("long", 1000.0, [-0.0002]) == 0.2)

check("negative funding flips: short pays",
      funding_pnl_usd("short", 1000.0, [-0.0002]) == -0.2)

check("multi-hour sums linearly",
      abs(funding_pnl_usd("long", 2000.0,
                          [0.0001, 0.0001, 0.0001]) - (-0.6)) < 1e-12)

check("zero rates accrue zero",
      funding_pnl_usd("short", 5000.0, [0.0, 0.0]) == 0.0)

# -- FundingLedger ---------------------------------------------------------

def funding_rows(coin, start_hour, rates):
    rows = []
    for i, r in enumerate(rates):
        rows.append({"coin": coin, "fundingRate": r,
                     "time": (start_hour + i) * 3_600_000})
    return rows


BASE_H = 483_000  # arbitrary hour bucket

fl = FundingLedger("https://x",
                   post=fake_post_factory(
                       funding_rows=funding_rows("BTC", BASE_H,
                                                [0.0001, 0.0002, 0.0003])))
got = fl.accrue("BTC", "long", 10_000.0,
                BASE_H * 3600.0, (BASE_H + 3) * 3600.0)
check("accrue 3 full hours long",
      abs(got - (-(0.0001 + 0.0002 + 0.0003) * 10_000.0)) < 1e-9, str(got))

got = fl.accrue("BTC", "short", 10_000.0,
                BASE_H * 3600.0, (BASE_H + 1.5) * 3600.0)
check("partial hour pro-rated for short",
      abs(got - (0.0001 * 10_000.0 + 0.5 * 0.0002 * 10_000.0)) < 1e-9,
      str(got))

check("empty window accrues zero",
      fl.accrue("BTC", "long", 10_000.0, 100.0, 100.0) == 0.0)

# cache: second accrue over the same hours must not refetch
calls = {"n": 0}


def counting_post(url, payload):
    calls["n"] += 1
    return funding_rows("ETH", BASE_H, [0.0001, 0.0001])


fl2 = FundingLedger("https://x", post=counting_post)
fl2.accrue("ETH", "long", 1000.0, BASE_H * 3600.0, (BASE_H + 2) * 3600.0)
fl2.accrue("ETH", "long", 1000.0, BASE_H * 3600.0, (BASE_H + 2) * 3600.0)
check("cache dedupes refetch", calls["n"] == 1, str(calls))

# failure path: fetch raises -> 0.0 accrued and a gap recorded
fl3 = FundingLedger("https://x",
                    post=fake_post_factory(fail=True))
got = fl3.accrue("SOL", "long", 5000.0, 1_000_000.0, 1_003_600.0)
check("failed fetch accrues 0.0", got == 0.0, str(got))
check("failed fetch records a gap", len(fl3.gaps) == 1, str(fl3.gaps))

# -- fee tier resolution -----------------------------------------------------

fees_fixture = {"userCrossRate": "0.00035", "userAddRate": "0.00008"}
rate, src = taker_fee_rate("https://x", account="0xabc",
                           post=fake_post_factory(fees=fees_fixture))
check("userFees taker parsed", abs(rate - 0.00035) < 1e-12, str(rate))
check("userFees source noted", "userFees" in src, src)

rate, src = maker_fee_rate("https://x", account="0xabc",
                           post=fake_post_factory(fees=fees_fixture))
check("userFees maker parsed", abs(rate - 0.00008) < 1e-12, str(rate))

rate, src = taker_fee_rate("https://x", account="0xabc",
                           post=fake_post_factory(fail=True))
check("failed userFees falls back to base",
      rate == BASE_TAKER_FEE and "failed" in src, f"{rate} {src}")

rate, src = taker_fee_rate("https://x", account=None)
check("no account -> base schedule, stated",
      rate == BASE_TAKER_FEE and "no account" in src, f"{rate} {src}")

# -- round_trip_costs --------------------------------------------------------

fl4 = FundingLedger("https://x", post=fake_post_factory(
    funding_rows=funding_rows("HYPE", BASE_H, [0.0005] * 6)))
fees, fund = round_trip_costs("long", 2.0, 100.0, 110.0,
                              BASE_H * 3600.0, (BASE_H + 5) * 3600.0,
                              "HYPE", 0.00045, fl4)
check("round-trip fees = taker on both notionals",
      abs(fees - 0.00045 * 2.0 * (100.0 + 110.0)) < 1e-9, str(fees))
check("round-trip funding signed negative for long",
      abs(fund - (-0.0005 * 5 * 200.0)) < 1e-9, str(fund))

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
