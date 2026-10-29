"""Keltner pullback risk config.

Pullback entries sit close to the midline, so the stop must
clear the pullback's own noise: 2xATR stop, 3xATR trail (let
the resumed trend run), no fixed target (the opposite midline
cross manages the trade), 120-bar (5-day) max hold -- a
pullback that has not resumed in five days was a reversal.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # EMA50 + Keltner EMA20/ATR10, with margin
