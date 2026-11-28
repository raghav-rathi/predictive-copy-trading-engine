"""Consecutive up/down days fade risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail,
no take-profit target, 24-bar max hold (a fade that has not
reverted within a day is not the setup), 1% risk/trade,
3x leverage cap.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 20  # streak counting + SMA(10) + ATR(14) + margin
