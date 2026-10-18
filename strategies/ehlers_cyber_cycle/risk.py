"""Cyber Cycle risk config: 2xATR hard stop, no trailing, no fixed target,
20-bar max hold (~half the dominant cycle Ehlers tunes the filter for,
so a trade that has not turned by then has missed the cycle)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=20,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
