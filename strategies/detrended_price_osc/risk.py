"""Detrended Price Oscillator risk config.

The DPO zero-line cross is the exit logic, so the harness
2xATR hard stop / 3xATR chandelier trail sit behind it as a
safety net for gap-through-cross moves. No take-profit
target — the trade rides the cycle until the opposite cross.
The 60-bar max hold keeps a position from camping through
sideways zero-line chop.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 35  # SMA(20) + 11-bar displacement, with margin
