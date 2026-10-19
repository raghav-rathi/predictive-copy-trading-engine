"""Kagi trend risk config.

The kagi yang/yin transitions do the trade management (exits on the
opposite transition), so there is no trailing and no fixed target. A
hard 2xATR stop covers gap/reversal shock, and a 100-bar max hold
prevents a thin/yin chop regime from camping in a dead position.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=100,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # kagi/ATR spin-up; thickness needs a few columns to form
