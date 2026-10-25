"""Classic pivot breakout risk config.

Pivot levels are tight (one bar's range), so the stop is the tighter
house variant: 1.5xATR stop, 2xATR trail, 72-bar (3-day) max hold — a
pivot breakout that hasn't run in three days is noise. Long/short
symmetric.
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

WARMUP = 20  # ATR(14) plus margin; pivots need only one prior bar
