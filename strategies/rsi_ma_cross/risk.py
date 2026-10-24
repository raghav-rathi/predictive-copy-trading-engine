"""RSI/MA cross risk config.

RSI crosses are fast momentum entries that whipsaw in chop, so
the stop is the house-standard 1.5xATR with a 2xATR chandelier
trail to lock in the momentum legs that do extend, and no fixed
target — the opposite cross is the exit. The 72-bar (~3-day) max
hold fits the thesis: an RSI cross that hasn't resolved in three
days was noise, not a momentum handoff. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # Wilder RSI(14) + SMA(14) spin-up, with margin
