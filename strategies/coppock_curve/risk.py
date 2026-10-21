"""Coppock Curve zero-cross risk config.

The zero-cross is a slow, smoothed momentum turn (ROC(14)+ROC(11)
through a 10-bar WMA), so the trade is expected to run as a swing:
the 2xATR hard stop covers reversal shock and the 3xATR chandelier
trail manages the swing; there is no fixed target because the
opposite cross is the natural exit. Max hold 200 bars keeps a dead
position from camping through a chop regime after the Coppock line
goes flat near zero.
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

WARMUP = 60  # ROC(14) spin-up + WMA(10) spin-up, with margin
