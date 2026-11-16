"""Dow Theory trend risk config.

The textbook stop sits below/above the last swing extreme (the last
swing low for a long, the last swing high for a short).  The harness
only supports an ATR-distance stop, so the swing-extreme stop is
approximated as 2xATR: on 1h crypto a 5-bar swing extreme typically
sits ~1.5-2.5xATR from the breakout entry, so 2xATR is the closest
fixed mapping and the stop is documented as an approximation, not
the literal swing level.  The 2R target (4xATR vs the 2xATR stop)
matches Dow's "let the primary trend run" intent: the target is far
enough that most exits are structure breaks (the signal exit), not
the target.  No chandelier trail -- a trail would cut the leg short
before the structure-break exit can fire.  Max hold 120 bars (~5
days) caps a leg that drifts sideways inside its range.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,    # ~ the last swing extreme (see docstring)
    trail_atr_mult=None,  # off: exits are structure-driven
    target_atr_mult=4.0,  # 2R vs the 2xATR stop
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # 5-bar pivots + volume mean spin-up, plus margin
