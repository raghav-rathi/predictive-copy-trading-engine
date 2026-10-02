#!/usr/bin/env python3
"""Reconciliation loop: the safety net for missed events.

Every N seconds (config mirror.reconcile_interval_s), fetch our
clearinghouseState and each COPY target's, and close drift:

  * target flat (or flipped sign) but we still hold  -> close 100%
  * we hold more than the target-implied size        -> close the excess
  * size drift within tolerance                      -> warn only

Reconcile only ever *reduces* risk: it never opens a position and never
increases one. It exists because websockets drop, fills get missed, and
the paper engine's target books are derived from the same event stream
it protects.

Fetch is implemented against the public POST /info endpoint (no auth).
TODO-verify: the exact clearinghouseState response shape against a live
call; parsing here is defensive and treats an unparseable response as
"no data" (skip the cycle, do not guess positions).
"""
from __future__ import annotations

import json
import sys
import urllib.request

EPS = 1e-9


def fetch_positions(info_url: str, user: str) -> dict[str, float]:
    """-> {coin: signed size}. Defensive; {} on anything unparseable."""
    payload = json.dumps({"type": "clearinghouseState",
                          "user": user}).encode()
    req = urllib.request.Request(
        info_url, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent": "predictive-copy-trading-engine/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r.read().decode())
    except Exception as e:  # network/API/shape failure: no data, not zero
        print(f"reconcile: clearinghouseState fetch failed for "
              f"{user[:10]}...: {e}", file=sys.stderr)
        return {}
    out: dict[str, float] = {}
    try:
        positions = (data.get("assetPositions") or [])
        for entry in positions:
            pos = entry.get("position") or {}
            coin = str(pos.get("coin", ""))
            size = float(pos.get("szi", 0) or 0)
            if coin and abs(size) > EPS:
                out[coin] = size
    except (TypeError, ValueError, AttributeError):
        return {}
    return out


def check_drift(our_positions: dict[tuple[str, str], dict],
                target_books: dict[str, dict[str, float]],
                tolerance_pct: float = 25.0) -> list[dict]:
    """Pure drift check -> list of close/reduce actions.

    our_positions: {(user, coin): {"size": signed, ...}}
    target_books:  {user: {coin: signed_size}}  (0/absent = flat)
    """
    actions: list[dict] = []
    for (user, coin), pos in our_positions.items():
        ours = float(pos.get("size", 0) or 0)
        if abs(ours) <= EPS:
            continue
        theirs = float((target_books.get(user) or {}).get(coin, 0.0))
        if abs(theirs) <= EPS:
            actions.append({"action": "close", "user": user, "coin": coin,
                            "pct": 1.0, "reason": "reconcile_flat",
                            "detail": "target flat, we hold"})
        elif (ours > 0) != (theirs > 0):
            actions.append({"action": "close", "user": user, "coin": coin,
                            "pct": 1.0, "reason": "reconcile_flip",
                            "detail": "target flipped sign"})
        else:
            # Proportional mirror implies our size should track theirs
            # within tolerance; only reduce, never add.
            drift = (abs(ours) - abs(theirs)) / max(abs(theirs), EPS) * 100.0
            if drift > tolerance_pct:
                excess = (abs(ours) - abs(theirs)) / abs(ours)
                actions.append({"action": "close", "user": user, "coin": coin,
                                "pct": round(min(excess, 1.0), 4),
                                "reason": "reconcile_drift",
                                "detail": f"we hold {drift:.1f}% over target"})
    return actions
