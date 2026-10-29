"""Abandoned baby risk config.

A reversal pattern with a natural invalidation (beyond the
doji extreme): 1.5xATR stop, 2xATR trail, 2.5xATR target
(reversals should pay quickly or not at all), 120-bar (5-day)
max hold. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=2.5,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # 20-bar volume average plus margin
