"""Three-line break risk config.

The line-break flips do the trade management (exits on the opposite
flip), so there is no trailing and no fixed target. A hard 2xATR stop
covers the case where a "turnaround" was just noise inside a larger
move, and a 60-bar max hold keeps dead positions from camping (a real
three-line-break trend should keep printing lines; a stalled one is a
failed signal).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # line-break spin-up; flips need a few lines to form
