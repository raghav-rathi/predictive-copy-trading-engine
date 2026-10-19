"""Laguerre RSI risk config -- mean-reversion: hard 2xATR stop, no
trailing (the centerline exit manages the trade), no fixed target,
50-bar max hold (Laguerre cycles resolve fast or they fail)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=50,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
