"""Hikkake risk config.

False-breakout patterns are quick resolution trades: either the trapped
side covers within a few bars or the pattern was noise. No trail (the
pattern edge is the initial squeeze, not a trend), 3xATR target /
1.5xATR stop = 2R, and a hard 20-bar max hold so a dead trade cannot
camp through a chop regime.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=3.0,
    max_hold_bars=20,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # inside-bar/trap structure + ATR spin-up
