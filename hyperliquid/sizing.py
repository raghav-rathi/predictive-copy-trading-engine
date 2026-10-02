#!/usr/bin/env python3
"""Sizing for the Hyperliquid copy engine.

Two rules, in this order:

1. Proportional mirror: copySize = fill.sz * multiplier, capped by
   max_position_usd and max_notional_per_trade_usd. This is the anchor;
   nothing ever sizes *above* it.

2. Fractional-Kelly cap from measured edge (stolen from jonny-traders):
   compute the Kelly fraction f* from the target's rolling realized
   closes (wins/losses in USD). The cap only ever *shrinks* the copy,
   and when measured edge <= 0 the open is skipped entirely. Copying a
   target with no proven edge is how you inherit someone else's losses
   — the fleet lesson, encoded.

f* = w - (1 - w) / (avg_win / avg_loss), with avg_win/avg_loss the mean
USD of winning/losing closes. Undefined (None) when there are too few
closes or no losing closes to measure risk against — in which case the
Kelly cap does not apply and the proportional cap stands alone.
"""
from __future__ import annotations

import statistics


def kelly_fstar(closes_usd: list[float], min_closes: int = 10) -> float | None:
    """Fractional-Kelly f* from realized closes (USD).

    Returns None when the edge is unmeasurable (too few closes, or no
    losing closes to measure downside against) — the Kelly cap then does
    not apply. Returns a negative number (here, -1.0) when the measured
    edge is negative (enough closes, none green): the caller must skip.
    """
    closes = [c for c in closes_usd if c != 0]
    if len(closes) < min_closes:
        return None  # insufficient data: edge unmeasurable, no Kelly cap
    wins = [c for c in closes if c > 0]
    losses = [-c for c in closes if c < 0]
    if not losses:
        return None  # no losing closes: downside unmeasurable, no Kelly cap
    if not wins:
        return -1.0  # measured negative edge: skip the open
    w = len(wins) / len(closes)
    b = statistics.mean(wins) / statistics.mean(losses)
    if b <= 0:
        return None
    return w - (1.0 - w) / b


def size_copy(fill_sz: float, fill_px: float, target_closes_usd: list[float],
              cfg: dict) -> tuple[float | None, dict]:
    """-> (size_in_coin or None, breakdown dict).

    Returns None when the copy should be skipped (measured edge <= 0).
    `target_closes_usd` is the target's rolling realized closes (USD),
    newest last; pass [] to disable the Kelly cap for this call.
    """
    m = cfg["mirror"]
    k = cfg["kelly"]
    notional = fill_sz * fill_px * m["multiplier"]
    cap = min(notional, m["max_position_usd"], m["max_notional_per_trade_usd"])
    breakdown = {"proportional_notional_usd": round(notional, 2),
                 "capped_notional_usd": round(cap, 2)}

    if k["enabled"] and target_closes_usd:
        recent = target_closes_usd[-k["rolling_closes"]:]
        f = kelly_fstar(recent, k["min_closes"])
        breakdown["kelly_fstar"] = None if f is None else round(f, 4)
        if f is not None and f <= 0:
            breakdown["decision"] = "skip: measured edge <= 0"
            return None, breakdown
        if f is not None:
            kelly_cap = f * k["fraction"] * m["max_position_usd"]
            breakdown["kelly_cap_usd"] = round(kelly_cap, 2)
            cap = min(cap, kelly_cap)
            breakdown["capped_notional_usd"] = round(cap, 2)

    breakdown["decision"] = "ok"
    size = cap / fill_px if fill_px > 0 else 0.0
    return size, breakdown
