#!/usr/bin/env python3
"""Honest cost accounting for the copy book.

STRATEGY_RESEARCH.md ideas 4a + 5 ("build now"): the engine's paper
ledger and backtest assumed taker entries with an unverified 0.035%
fee and *zero* funding payments. Hyperliquid funding is positive
~99% of hours on majors, so every copied long systematically pays
~10% APR and every copied short earns it. At our ~5h average hold
that is ~0.006%/trade of unmodeled drag on longs — small per trade,
systematic across the book, and currently invisible in the track
record. The backtest's 0.035% taker assumption is also *below* the
documented 0.045% base rate (verified live via the `userFees` info
endpoint), i.e. optimistic.

This module provides, paper-first and stdlib-only:

  * `taker_fee_rate(info_url, account=None)` — the real tiered taker
    fee for a configured account via `userFees` (`userCrossRate`);
    falls back to the documented base schedule (0.045% taker /
    0.015% maker) when no account is configured or the endpoint
    fails. No account = no guess: the fallback is the public
    schedule, and the source used is always reported.
  * `FundingLedger` — hourly funding accrual over a held position.
    Sign convention: Hyperliquid funding is paid hourly, positive
    rate => longs pay shorts.  funding_pnl = -side_sign * rate *
    notional, summed per hour (last partial hour pro-rated).
    Rates come from the public `fundingHistory` endpoint, cached
    per (coin, hour); a failed fetch accrues 0.0 and records the
    gap instead of silently succeeding.
  * `round_trip_costs(...)` — one helper returning (fees_usd,
    funding_usd) for a closed leg so ledgers can attribute them
    separately from price PnL.

Nothing here touches live execution: it is pure accounting used by
the paper ledger (hyperliquid/paper.py) and offline analysis.
"""
from __future__ import annotations

import json
import math
import urllib.request

# Documented Hyperliquid base schedule (verified 2026-10-08 via the
# `userFees` info endpoint for a zero-volume account: cross 0.00045,
# add 0.00015). Tiers lower it by 14d volume; HYPE staking and
# referral add discounts on top.
BASE_TAKER_FEE = 0.00045
BASE_MAKER_FEE = 0.00015

INFO_TIMEOUT_S = 15


def _post(info_url: str, payload: dict,
          post=None) -> object:
    if post is not None:
        return post(info_url, payload)
    req = urllib.request.Request(
        info_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=INFO_TIMEOUT_S) as resp:
        return json.load(resp)


def taker_fee_rate(info_url: str, account: str | None = None,
                   post=None) -> tuple[float, str]:
    """Return (taker_fee_fraction, source_note).

    With `account` set, resolves the real tiered rate from `userFees`
    (userCrossRate). Otherwise returns the documented base schedule.
    Never raises: on any failure returns the base schedule and says so.
    """
    if account:
        try:
            data = _post(info_url, {"type": "userFees", "user": account},
                         post=post)
            rate = float(data["userCrossRate"])
            if rate >= 0:
                return rate, f"userFees tier for {account[:10]}..."
        except Exception as exc:  # noqa: BLE001 - fail safe, report
            return BASE_TAKER_FEE, \
                f"base schedule (userFees failed: {type(exc).__name__})"
    return BASE_TAKER_FEE, "base schedule (no account configured)"


def maker_fee_rate(info_url: str, account: str | None = None,
                   post=None) -> tuple[float, str]:
    """Same as taker_fee_rate for the maker (add-liquidity) rate."""
    if account:
        try:
            data = _post(info_url, {"type": "userFees", "user": account},
                         post=post)
            rate = float(data["userAddRate"])
            if rate >= 0:
                return rate, f"userFees tier for {account[:10]}..."
        except Exception as exc:  # noqa: BLE001 - fail safe, report
            return BASE_MAKER_FEE, \
                f"base schedule (userFees failed: {type(exc).__name__})"
    return BASE_MAKER_FEE, "base schedule (no account configured)"


def funding_pnl_usd(side: str, notional_usd: float,
                    hourly_rates: list[float]) -> float:
    """Signed funding PnL for one position over a list of hourly rates.

    Positive funding rate => longs pay shorts.  Longs (side "long",
    sign +1) lose rate*notional per hour; shorts (sign -1) gain it.
    Returns USD, positive when the position *earns* funding.
    """
    sign = 1.0 if side == "long" else -1.0
    return sum(-sign * r * notional_usd for r in hourly_rates)


class FundingLedger:
    """Accrues hourly funding payments for held paper positions.

    Rates are fetched once per (coin, hour-bucket) from the public
    `fundingHistory` endpoint and cached, so a replay with many closes
    costs one HTTP call per coin per distinct hour. A failed or empty
    fetch accrues 0.0 for those hours and appends the window to
    `gaps` — never silently treated as zero funding without a record.
    """

    def __init__(self, info_url: str, post=None):
        self.info_url = info_url
        self.post = post
        self._cache: dict[tuple[str, int], float] = {}
        self.gaps: list[tuple[str, int, int]] = []

    def _fetch_window(self, coin: str, start_ms: int,
                      end_ms: int) -> None:
        try:
            data = _post(self.info_url,
                         {"type": "fundingHistory", "coin": coin,
                          "startTime": start_ms, "endTime": end_ms},
                         post=self.post)
        except Exception:  # noqa: BLE001 - recorded as a gap below
            data = None
        rows = data or []
        for row in rows:
            try:
                hour = int(row["time"]) // 3_600_000
                self._cache[(row["coin"], hour)] = float(row["fundingRate"])
            except (KeyError, TypeError, ValueError):
                continue
        if not rows:
            self.gaps.append((coin, start_ms, end_ms))

    def hourly_rates(self, coin: str, entry_ts_s: float,
                     exit_ts_s: float) -> list[float]:
        """Hourly funding rates in effect while the position was held.

        The last partial hour is pro-rated by the fraction held, so a
        5.5h hold accrues 5 full hours + 0.5 of the sixth.
        """
        if exit_ts_s <= entry_ts_s:
            return []
        start_ms = int(entry_ts_s * 1000)
        end_ms = int(exit_ts_s * 1000)
        first_hour = start_ms // 3_600_000
        last_hour = (end_ms - 1) // 3_600_000
        missing = [h for h in range(first_hour, last_hour + 1)
                   if (coin, h) not in self._cache]
        if missing:
            self._fetch_window(coin, missing[0] * 3_600_000,
                               (missing[-1] + 1) * 3_600_000)
        rates = [self._cache.get((coin, h), 0.0)
                 for h in range(first_hour, last_hour + 1)]
        # Pro-rate the final partial hour.
        span_h = (exit_ts_s - entry_ts_s) / 3600.0
        full, frac = divmod(span_h, 1.0)
        if rates and frac > 1e-9 and full < len(rates):
            rates = rates[: int(full)] + [rates[int(full)] * frac]
        elif rates:
            rates = rates[: max(int(math.ceil(span_h)), 1)]
        return rates

    def accrue(self, coin: str, side: str, notional_usd: float,
               entry_ts_s: float, exit_ts_s: float) -> float:
        """Signed funding PnL in USD for one held leg."""
        return funding_pnl_usd(side, notional_usd,
                               self.hourly_rates(coin, entry_ts_s,
                                                 exit_ts_s))


def round_trip_costs(side: str, size: float, entry_px: float,
                     exit_px: float, entry_ts_s: float, exit_ts_s: float,
                     coin: str, taker_fee: float,
                     funding: FundingLedger) -> tuple[float, float]:
    """Return (fees_usd, funding_usd) for a closed leg.

    Fees: taker rate on entry notional + exit notional (IOC-style
    execution, matching mirror.py). Funding: hourly accrual over the
    hold, signed (positive = earned). Both are costs to *subtract*
    from price PnL except earned funding, which adds.
    """
    fees = taker_fee * size * (entry_px + exit_px)
    funding_pnl = funding.accrue(coin, side, size * entry_px,
                                 entry_ts_s, exit_ts_s)
    return fees, funding_pnl
