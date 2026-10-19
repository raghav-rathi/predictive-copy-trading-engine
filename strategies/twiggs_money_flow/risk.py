"""Twiggs Money Flow risk config -- zero-line-cross momentum system: hard
2xATR stop, no trailing/target (the zero-line cross-back exits manage the
trade), 60-bar max hold to keep dead money-flow drifts from camping."""

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

WARMUP = 80
