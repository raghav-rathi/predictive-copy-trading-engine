"""Fibonacci pullback risk config -- swing-target system: hard 2xATR
stop (approximation of the 78.6% invalidation level beyond the pocket,
which the harness cannot place as a level stop), the swing-high/low
signal exit takes profit at the prior swing extreme, 100-bar max hold
to keep dead pullbacks from camping."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=100,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 260
