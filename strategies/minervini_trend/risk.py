"""Minervini risk config — trend-template longs are slow position
trades: 2xATR hard stop, 3xATR chandelier trail, 720-bar (30d) max hold.
LONG ONLY. WARMUP 4900 leaves only ~258 tradeable bars out of 5,158 —
the tradeable sample is tiny by construction (see CALIBRATION.md)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=720,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 4900
