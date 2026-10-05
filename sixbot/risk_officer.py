"""BOT 3 - RISK OFFICER.

Position sizing. It NEVER looks at charts - only numbers:
account equity, entry price, stop price, risk%.

An add is approved ONLY if the previous entry on that coin is at breakeven
(its stop has been moved to its entry price).
"""
from dataclasses import dataclass

from .config import get


@dataclass
class Size:
    qty: float
    notional: float
    risk_amount: float
    risk_pct: float


@dataclass
class Position:
    coin: str
    entry: float          # initial entry (breakeven reference)
    avg_entry: float      # average entry incl. adds (PnL reference)
    stop: float           # current stop (zone top, or entry once at breakeven)
    zone_top: float
    zone_bottom: float
    anchor_high: float
    qty: float
    risk_dist: float      # zone_top - entry at inception (R accounting)
    risked: float         # total USD risked (initial + adds)
    alert_id: str = ""
    prime: bool = False
    skip_flag: str = ""   # gate skip flag carried for the auditor's split
    fee_entry: float = 0.0
    slip_entry: float = 0.0
    adds: int = 0
    entry_ms: int = 0
    breakeven: bool = False

    def at_breakeven(self):
        return self.breakeven


def size_position(equity, entry, stop, risk_pct):
    """Pure sizing math. Returns Size or None (INVALID_SIZE)."""
    if stop <= entry or entry <= 0 or equity <= 0:
        return None
    risk_amount = equity * risk_pct / 100.0
    qty = risk_amount / (stop - entry)
    return Size(qty=qty, notional=qty * entry,
                risk_amount=risk_amount, risk_pct=risk_pct)


def size_initial(equity, entry, stop):
    return size_position(equity, entry, stop, get("RISK_PCT_INITIAL"))


def add_approved(position):
    """An add is approved ONLY if the previous entry is at breakeven."""
    return (position.at_breakeven()
            and position.adds < get("MAX_ADDS_PER_POSITION"))


def size_add(equity, add_entry, breakeven_stop):
    """Each add = RISK_PCT_ADD, stopped at the original breakeven."""
    return size_position(equity, add_entry, breakeven_stop,
                         get("RISK_PCT_ADD"))
