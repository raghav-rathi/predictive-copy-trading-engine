"""Wyckoff spring risk config — the shakeout low/high IS the natural
invalidation, so a tight 1xATR stop sits just beyond it; the opposite
range edge is the objective (signal exit), no trailing, 120-bar max
hold for slow range resolution."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 70
