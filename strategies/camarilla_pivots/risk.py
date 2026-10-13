"""Camarilla risk.

Fade mode targets the pivot mid via signal exits. The published method
stops fades at R4/S4; a static ATR stop cannot express that exactly
(R3->R4 ~= 0.275 * prior-day range, a daily-scale distance), so risk.py
uses a wide 3.0xATR hard stop as disaster protection and max_hold 48h
to kill stale fades. No trailing: the mid target is the exit logic.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=3.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 72  # need 2 full UTC sessions for prior-day stats
