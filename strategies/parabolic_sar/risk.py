"""Parabolic SAR risk config -- the SAR itself is the trailing stop, so the
hard stop is wide (3xATR safety only), no extra trailing or target, no
max hold: a stop-and-reverse system lives or dies by its flips."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=3.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40
