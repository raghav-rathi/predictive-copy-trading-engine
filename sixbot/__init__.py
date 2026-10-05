"""Six-bot trading desk (paper mode only).

Implements the six charters in DESK_RULES.md — the single source of truth:

    screener.py      BOT 1 - daily three-candle flip detector (short-only)
    cartographer.py  BOT 2 - 4H Fair Value Gap ladder from anchor high to low
    risk_officer.py  BOT 3 - position sizing; never looks at charts
    gate.py          BOT 4 - emits alerts only; NEVER places orders
    exit_clerk.py    BOT 5 - manages open positions on 4H / daily closes
    auditor.py       BOT 6 - journals trades + skipped alerts, grades vs
                     the locked go/no-go thresholds
    executor.py      live-order entry point: raises NotImplementedError
                     by design. Paper mode only, like the rest of this repo.

Pipeline:
    daily candles -> screener -> cartographer -> risk_officer -> gate
        -> (paper fills in backtest.py) -> exit_clerk -> auditor
"""
from .config import PARAMS, get

__all__ = ["PARAMS", "get"]
