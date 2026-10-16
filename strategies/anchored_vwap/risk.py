"""Anchored VWAP risk config — reclaims get a hard 2xATR stop (a failed
reclaim is immediately wrong), a wide 3xATR chandelier trail to ride the
leg the line identifies, no fixed target, 72-bar max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
