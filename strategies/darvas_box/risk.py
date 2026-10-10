"""Darvas Box risk config — long-only.

Darvas' own rule was a tight stop just under the box floor, and that is the
signal-level exit in signals.py (long_exit on close below the box bottom).
The 1.5xATR hard stop is a safety net only; no trailing/target/max-hold —
the box floor manages the trade."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 100
