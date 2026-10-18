"""Bill Williams' Alligator + fractal risk config -- 1.5xATR hard stop as the
harness-supported approximation of a fractal-extreme stop (a true Williams
stop sits just beyond the most recent opposite fractal; the event-driven
harness only models ATR-distance stops, so 1.5xATR stands in), no trailing
(the sleep/fractal exit does the trade management), no fixed target, 72-bar
max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80
