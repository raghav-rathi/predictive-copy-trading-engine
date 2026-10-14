"""Stochastic-hook risk config -- pullback entries with trend bias get a
2xATR stop and 48-bar max hold; no target, the cross-against exit does
the trade management."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
