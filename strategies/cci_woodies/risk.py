"""Woodies CCI risk config -- hook-then-zero-line is a quick mean-reversion
trade: 2xATR hard stop, no trail, no fixed target, 48-bar (2-day) max
hold, both sides."""

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

WARMUP = 60
