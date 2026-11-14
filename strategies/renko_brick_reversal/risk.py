"""Renko 2-brick reversal risk config.

Renko entries are trend-reversal entries: the position needs room
for the new brick run to develop, so the max hold is long (200
bars, ~8 days) and the 3xATR chandelier trail does the lifting once
a leg extends. The 2xATR hard stop handles the failure case -- a
2-brick reversal that rolls straight back over is a failed reversal,
so a tight stop keeps those losers small. No fixed target -- Renko
exits are reversal-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 220  # brick-size window (200 bars) + brick formation, with margin
