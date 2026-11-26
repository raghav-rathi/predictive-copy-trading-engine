"""Connors TPS risk config.

House standard except max_hold_bars=10: the 10-bar time exit
is part of the system (the book's day-11 exit, scaled to 1h),
so the harness max-hold enforces it rather than the generic
120-bar cap. 2xATR hard stop, 3xATR chandelier trail, no
take-profit target, 1% risk per trade, 3x leverage cap.

The original Connors system has no stop — the 2xATR stop /
3xATR trail is added as a deviation required by house risk
rules.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=10,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# SMA(200) spin-up, with margin.
WARMUP = 210
