"""BOT 5 - EXIT CLERK.

Manages open positions on 4H and daily closes. No discretion.

  - 4H: price trades at/through the stop (zone top) -> EXIT at the stop.
        Evaluated intrabar on 4H highs; fill assumed at the stop price.
  - Daily: a daily close above the anchor (anchor high) -> EXIT immediately
        at the close. Catastrophic-invalidation backstop.
  - In profit with no exit signal: state NEUTRAL -> hold. No discretionary
    exits, no trailing, no take-profit in this charter.
  - Flat for STALE_HOURS with max favorable excursion < STALE_MIN_MOVE_R ->
    flag STALE, exit at market.
  - Breakeven: once price moves 1R in favor, move the stop to the entry.
    (This is what unlocks adds under the Risk Officer.)
"""
from dataclasses import dataclass

from .config import get


@dataclass
class ExitSignal:
    action: str      # "EXIT" | "HOLD" | "MOVE_BE"
    reason: str = ""  # STOP | ANCHOR | STALE | ""
    price: float = 0.0


def check_4h(position, candle):
    """Evaluate one closed 4H candle (intrabar stop on its high)."""
    if candle["h"] >= position.stop:
        return ExitSignal("EXIT", "STOP", position.stop)
    return ExitSignal("HOLD")


def check_daily(position, candle, anchor_high):
    """Evaluate one closed daily candle."""
    if candle["c"] > anchor_high:
        return ExitSignal("EXIT", "ANCHOR", candle["c"])
    return ExitSignal("HOLD")


def check_stale(position, now_ms, mfe_r):
    """STALE flag: flat for STALE_HOURS with MFE < STALE_MIN_MOVE_R."""
    age_h = (now_ms - position.entry_ms) / 3600_000
    if age_h >= get("STALE_HOURS") and mfe_r < get("STALE_MIN_MOVE_R"):
        return ExitSignal("EXIT", "STALE", 0.0)  # price filled by caller
    return ExitSignal("HOLD")


def maybe_move_breakeven(position, mfe_r):
    """Once price moves 1R in favor, stop -> entry (breakeven)."""
    if not position.breakeven and mfe_r >= 1.0:
        return ExitSignal("MOVE_BE")
    return ExitSignal("HOLD")


def state_in_profit(unrealized):
    """NEUTRAL while in profit -> hold (the no-discretion guardrail)."""
    return "NEUTRAL" if unrealized > 0 else "UNDERWATER"
