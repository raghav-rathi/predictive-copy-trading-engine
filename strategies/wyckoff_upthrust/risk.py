"""Wyckoff upthrust risk config (standard batch risk layer, short-only)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=False,
    allow_shorts=True,
)

# Range window 20 (prior bars) + shift; +5 margin.
WARMUP = 25
