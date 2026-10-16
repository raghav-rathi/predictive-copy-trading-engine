"""Raschke Tail risk config — the pattern is a reversal off a fresh
extreme: 2xATR hard stop, 3xATR chandelier trail to ride the snapback,
48-bar max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
