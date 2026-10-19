"""Fractal breakout risk config -- breakout system: hard 2xATR stop
(false breakouts are the dominant loss mode, so the stop is structural,
not optional), no trailing/target (the fractal-level exit manages the
trade), 80-bar max hold to keep stale breakouts from camping."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=80,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 260
