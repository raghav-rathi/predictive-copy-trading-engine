"""Envelope breakout risk config.

House standard for a breakout system: 2xATR stop, 2.5xATR chandelier
trail, no fixed target (the midline exit manages the trade), 120-bar
(5-day) max hold. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # SMA(20) plus margin
