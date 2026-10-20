"""Kalman filter trend risk config.

The kf cross manages the trend (exits on the opposite cross), so there
is no trailing and no fixed target. A hard 2xATR stop covers
gap/reversal shock, and a 200-bar max hold prevents a flat-filter
regime from camping in a dead position while the filter drifts
sideways with price.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # Kalman filter + ATR spin-up
