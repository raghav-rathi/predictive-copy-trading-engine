"""Pivot breakout risk config -- failed-breakout aware spec: 2xATR hard
stop (the primary defense against whipsaw fakeouts through R1/S1), no
trailing and no fixed target (the opposite-side touch exit does the
trade management), 5-day (120-bar) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100
