#!/usr/bin/env python3
"""Sell-back (exit-liquidity) check: the honeypot rule, adapted to perps.

Slime Family rule: a coin must be sellable for >= 80% of its buy price.
For Hyperliquid perps the equivalent is: an immediate full exit of the
proposed position into the CURRENT order book must recover >= 80% of
the entry notional. A trade into a thin book is refused, however good
the thesis looks.

Unit-testable: pass any dict-shaped book; no network required.
A Hyperliquid public-API book feed is included for live runs (no keys).
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass
class SellbackConfig:
    min_recovery_pct: float = 80.0   # must recover >= 80% on instant exit
    fee_buffer_pct: float = 0.11     # 0.055% per side, both sides


class BookFeed(Protocol):
    def get_book(self, coin: str) -> dict | None: ...


def sellback_ok(coin: str, side: str, size_usd: float,
                book: dict | None,
                cfg: SellbackConfig = SellbackConfig()) \
        -> tuple[bool, dict]:
    """-> (ok, detail). `book` = {"bids": [(px, qty), ...],
    "asks": [(px, qty), ...], "mid": px}. Exit side: longs sell into
    bids, shorts buy into asks. Returns the estimated proceeds and the
    recovery ratio vs entry notional."""
    detail: dict = {"coin": coin, "side": side, "size_usd": size_usd,
                    "proceeds_usd": 0.0, "recovery_pct": 0.0,
                    "reason": ""}
    if not book:
        detail["reason"] = "no_book"
        return False, detail
    levels = book.get("bids" if side == "long" else "asks") or []
    if not levels:
        detail["reason"] = "empty_book_side"
        return False, detail
    remaining = float(size_usd)
    proceeds = 0.0
    for px, qty in levels:
        px, qty = float(px), float(qty)
        if px <= 0 or qty <= 0:
            continue
        take = min(remaining, px * qty)
        proceeds += take
        remaining -= take
        if remaining <= 1e-9:
            break
    if remaining > 1e-9:
        detail["reason"] = (f"insufficient_depth: "
                            f"${remaining:,.0f} unfilled")
        detail["proceeds_usd"] = round(proceeds, 2)
        return False, detail
    # fees on both sides of the round trip
    net = proceeds * (1.0 - cfg.fee_buffer_pct / 100.0)
    recovery = net / size_usd * 100.0 if size_usd > 0 else 0.0
    detail["proceeds_usd"] = round(net, 2)
    detail["recovery_pct"] = round(recovery, 2)
    ok = recovery >= cfg.min_recovery_pct
    if not ok:
        detail["reason"] = (f"thin_book: recovery {recovery:.1f}% < "
                            f"{cfg.min_recovery_pct:.0f}% min")
    return ok, detail


class StubBookFeed:
    """Deterministic in-memory books for tests and demos."""
    def __init__(self, books: dict[str, dict]):
        self.books = books

    def get_book(self, coin: str) -> dict | None:
        return self.books.get(coin.upper())


def _hl_post(payload: dict, timeout: int = 15) -> dict:
    req = urllib.request.Request(
        "https://api.hyperliquid.xyz/info",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class HyperliquidBookFeed:
    """Real L2 books from the Hyperliquid public API. No keys needed."""
    def get_book(self, coin: str) -> dict | None:
        try:
            data = _hl_post({"type": "l2Book", "coin": coin.upper()})
            bids = [(float(l["px"]), float(l["sz"]))
                    for l in data.get("levels", [[], []])[0]]
            asks = [(float(l["px"]), float(l["sz"]))
                    for l in data.get("levels", [[], []])[1]]
            mids = _hl_post({"type": "allMids"})
            mid = float(mids.get(coin.upper(), 0) or 0)
            return {"bids": bids, "asks": asks, "mid": mid}
        except Exception:
            return None
