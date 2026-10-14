"""VWAP reversion risk: the target IS the VWAP (exit signal handles it),
so no ATR target; 1.5xATR stop for the days it doesn't revert, 24-bar
(1-day on 1h) max hold — never carry a stale intraday bet overnight."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
