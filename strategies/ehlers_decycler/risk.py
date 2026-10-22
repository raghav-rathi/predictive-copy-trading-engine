"""Decycler risk config.

The decycler is a trend-component tracker with inherently fast
crosses: price crosses the lag-free line often, so whipsaw is the
enemy and holding time should be moderate (150 bars, ~6 days). A
2xATR hard stop plus a 2xATR chandelier trail keep chop losses small
and let genuine trend legs breathe. No fixed target — decycler exits
are cross-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # Butterworth filter + ATR spin-up, with margin
