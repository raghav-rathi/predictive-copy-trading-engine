"""Squeeze risk: expansion moves are fast — take profit at 3xATR, stop at
1.5xATR, and don't overstay: 72-bar (3-day on 1h) max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=3.0,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
