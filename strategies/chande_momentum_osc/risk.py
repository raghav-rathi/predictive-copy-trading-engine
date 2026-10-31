"""Chande Momentum Oscillator risk config (standard batch risk layer)."""

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
    allow_longs=True,
    allow_shorts=True,
)

# CMO(14) needs 15 bars (14 changes); ATR(14) needs 14.
# WARMUP = 20 covers both with margin.
WARMUP = 20
