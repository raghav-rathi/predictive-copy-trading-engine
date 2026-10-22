"""Reflex zero-cross risk config.

Reflex is a fast zero-lag turn detector: zero crosses fire at the
turn itself, so positions are held for the leg that follows, not for
the cross. The 2.5xATR chandelier trail gives a developing leg room
to extend while the 2xATR hard stop cuts the common failure case --
a cross that immediately re-crosses is Reflex whipsawing in chop,
and those trades want to die small. The 150-bar max hold (~6 days)
bounds the no-exit tail without starving trend legs; no fixed
target — Reflex exits are cross-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # SuperSmoother(20) transient + length-20 shift lookback, with margin
