"""Ichimoku risk: cloud systems are slow — 2.5xATR stop, 3xATR chandelier
trailing, no fixed target; Tenkan/Kijun crosses and Kijun breaks exit."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
