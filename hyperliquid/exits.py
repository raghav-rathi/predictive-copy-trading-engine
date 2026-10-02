#!/usr/bin/env python3
"""Exit rules for the Hyperliquid copy engine — independent hard stops.

Exits are the easy-to-forget half of copy trading. The Robinhood Chain
fleet's losses were mostly an exit problem (median ~51 min holds into
names that bled -30...-90%), so this engine carries exits that fire
regardless of what the target does. First trigger wins:

  1. target_exit   -- the copied target closed (proportional, via mirror)
  2. stop_loss     -- adverse move of stop_loss_pct from entry (side-aware)
  3. trailing_stop -- giveback of trailing_stop_pct from the peak
                     favorable move; the stop ratchets up with the
                     position and never loosens (kei_4650)
  4. take_profit   -- favorable move of take_profit_pct from entry
  5. max_hold      -- max_hold_seconds elapsed (backstop)
  6. max_age       -- max_position_age_seconds elapsed: a tighter
                     lifetime cap on every position (kei_4650's
                     lifetime exits, sized for perps in hours)

A copier is never left bagholding a loser target's position overnight.

`synced_close_size` is the pre-close state sync (Dwellir's CRITICAL
point): re-read our size from the authoritative source immediately
before a reduce-only close, instead of trusting a possibly stale
cached value. In live mode that source is a fresh clearinghouseState
fetch; in paper mode the ledger is the source.
"""
from __future__ import annotations


def synced_close_size(get_size, coin: str) -> float:
    """Authoritative pre-close size read -> |size| in coin units.

    `get_size(coin)` must return our current signed size for the coin
    from the freshest source available. Never raises: on failure it
    returns 0.0 (the close becomes a no-op rather than a guess).
    """
    try:
        return abs(float(get_size(coin) or 0.0))
    except Exception:
        return 0.0


class ExitManager:
    def __init__(self, stop_loss_pct: float, take_profit_pct: float,
                 max_hold_seconds: float, trailing_stop_pct: float = 0.0,
                 max_position_age_seconds: float = float("inf")):
        for name, v in (("stop_loss_pct", stop_loss_pct),
                        ("take_profit_pct", take_profit_pct),
                        ("max_hold_seconds", max_hold_seconds)):
            if v <= 0:
                raise ValueError(f"{name} must be > 0")
        if trailing_stop_pct < 0:
            raise ValueError("trailing_stop_pct must be >= 0")
        if max_position_age_seconds <= 0:
            raise ValueError("max_position_age_seconds must be > 0")
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_hold_seconds = max_hold_seconds
        self.trailing_stop_pct = trailing_stop_pct
        self.max_position_age_seconds = max_position_age_seconds
        # Per-position peak favorable move (pct), keyed by caller key
        # (e.g. (user, coin)). Drives the trailing stop.
        self._peaks: dict = {}

    def check(self, key, side: str, entry_px: float, entry_ts: float,
              mark_px: float | None, now: float) -> str | None:
        """-> exit reason, or None if the position survives.

        `side` is "long" or "short" — all pct math is side-aware, so a
        short's favorable move (mark falling) never trips its stop.
        """
        if entry_px <= 0 or mark_px is None:
            return None  # cannot price it; never guess an exit price
        raw = (mark_px / entry_px - 1.0) * 100.0
        move = raw if side == "long" else -raw  # favorable-positive
        peak = self._peaks.get(key, move)
        peak = max(peak, move)
        self._peaks[key] = peak
        if move <= -self.stop_loss_pct:
            return "stop_loss"
        if self.trailing_stop_pct > 0 and move <= peak - self.trailing_stop_pct:
            return "trailing_stop"
        if move >= self.take_profit_pct:
            return "take_profit"
        if now - entry_ts >= self.max_hold_seconds:
            return "max_hold"
        if now - entry_ts >= self.max_position_age_seconds:
            return "max_age"
        return None

    def forget(self, key) -> None:
        """Drop trailing state for a fully closed position."""
        self._peaks.pop(key, None)
