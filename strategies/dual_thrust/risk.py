"""Dual Thrust risk config -- classic intraday spec: 2xATR hard stop, no
trailing and no fixed target (the reversing exit does the trade
management), 24-bar (one session) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 150
