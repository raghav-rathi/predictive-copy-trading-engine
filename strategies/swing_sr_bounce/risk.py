"""Swing support / resistance bounce risk config.

Bounces are quick trades: the tighter house variant — 1.5xATR stop,
2xATR trail, 72-bar (3-day) max hold. A bounce that hasn't bounced in
three days is a level that broke. Long/short symmetric.
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

WARMUP = 100  # several zigzag pivots of spin-up, with margin
