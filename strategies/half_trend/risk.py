"""HalfTrend risk config -- ATR(100)-scale trend follower: 2xATR hard
stop, 3xATR chandelier trail, 240-bar (10-day) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 110  # amplitude(50) + ATR(100) need 100 bars; margin for stability
