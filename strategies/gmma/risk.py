"""GMMA risk config -- trend-following exits via the recross in
signals.py, so the stop is a wider 2xATR hard stop, a 2.5xATR chandelier
trail rides the trend legs, no fixed target, no max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100
