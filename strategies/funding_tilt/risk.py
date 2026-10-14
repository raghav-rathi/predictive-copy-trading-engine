"""Funding tilt risk: contrarian entries need a stop because crowding can
persist; 2xATR stop, 2xATR target (mean-reversion of positioning),
72-bar max hold so stale tilts don't linger."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 200
