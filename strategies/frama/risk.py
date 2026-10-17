"""FRAMA risk config -- fractal-adaptive trend follower: 2xATR hard
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

WARMUP = 110  # FRAMA(16) + SMA(100) need 100 bars; margin for stability
