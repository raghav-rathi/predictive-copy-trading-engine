"""Triple-EMA stack risk config.

A trend system: roomy 2xATR stop, 3xATR chandelier trail, no
fixed target (the unstack exit manages the trade), 336-bar
(14-day) max hold. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=336,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # EMA(21) plus margin
