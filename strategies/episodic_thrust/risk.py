"""Episodic-pivot risk config — thrust entries are violent by design:
2xATR stop, 3xATR chandelier trail, 30-bar max hold, longs only."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=30,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 120
