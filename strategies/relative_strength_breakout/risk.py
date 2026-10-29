"""Relative-strength breakout risk config.

Breakout trades on a ratio line are noisy: 2xATR stop, 2.5xATR
trail, no fixed target (the fade back through the ratio mean
manages the trade), 168-bar (7-day) max hold. Long/short
symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # 20-bar ratio range plus margin
