"""Ribbon-trend risk config -- alignment trend posture: 2xATR hard
stop, 3xATR chandelier trail, 168-bar (7-day) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 70  # EMA(55) needs 55 bars; margin for stability
