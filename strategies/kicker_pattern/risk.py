"""Kicker pattern risk config.

A kicker is a violent gap reversal, so the stop is roomy (2xATR)
and the trail is 2.5xATR; no fixed target (the opposite-kicker
exit manages the trade). 72-bar (3-day) max hold: a gap reversal
that has not followed through in three days was noise, not a
regime change. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 20  # ATR(14) plus margin; the pattern itself needs 2 bars
