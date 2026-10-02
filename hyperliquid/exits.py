#!/usr/bin/env python3
"""Exit rules for the Hyperliquid copy engine — independent hard stops.

Exits are the easy-to-forget half of copy trading. The Robinhood Chain
fleet's losses were mostly an exit problem (median ~51 min holds into
names that bled -30...-90%), so this engine carries exits that fire
regardless of what the target does. First trigger wins:

  1. target_exit   -- the copied target closed (proportional, via mirror)
  2. stop_loss     -- position down stop_loss_pct from entry
  3. take_profit   -- position up take_profit_pct from entry
  4. max_hold      -- max_hold_seconds elapsed, whatever the PnL

A copier is never left bagholding a loser target's position overnight.
"""
from __future__ import annotations


class ExitManager:
    def __init__(self, stop_loss_pct: float, take_profit_pct: float,
                 max_hold_seconds: float):
        for name, v in (("stop_loss_pct", stop_loss_pct),
                        ("take_profit_pct", take_profit_pct),
                        ("max_hold_seconds", max_hold_seconds)):
            if v <= 0:
                raise ValueError(f"{name} must be > 0")
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_hold_seconds = max_hold_seconds

    def check(self, entry_px: float, entry_ts: float, mark_px: float,
              now: float) -> str | None:
        """-> exit reason, or None if the position survives."""
        if entry_px <= 0 or mark_px is None:
            return None  # cannot price it; never guess an exit price
        change_pct = (mark_px / entry_px - 1.0) * 100.0
        if change_pct <= -self.stop_loss_pct:
            return "stop_loss"
        if change_pct >= self.take_profit_pct:
            return "take_profit"
        if now - entry_ts >= self.max_hold_seconds:
            return "max_hold"
        return None
