"""Turtle Soup risk config -- Raschke-style tight fade: 1.5xATR stop,
2.0xATR chandelier trail, 2.5xATR target (fade profits are capped),
24-bar max hold so stale traps don't linger."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=2.5,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
