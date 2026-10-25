"""Wedge breakout risk config.

Reversal-pattern standard: 2xATR stop, 2.5xATR chandelier trail, no
fixed target (the reclaim exit manages the trade), 96-bar (4-day)
max hold. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # several zigzag pivots of spin-up, with margin
