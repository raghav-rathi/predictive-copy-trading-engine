"""Instantaneous Trendline risk config.

Price vs the trendline is the entry/exit trigger, so the
harness stop is a backstop only: 2xATR(14). No trail, no
target — the method rides the trendline until price crosses
back through it or the line turns. 168-bar (~7-day) max hold
caps a stale trend ride. 1% risk per trade, 3x leverage cap.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# Filter settles in a handful of bars; 30 bars is ample margin.
WARMUP = 30
