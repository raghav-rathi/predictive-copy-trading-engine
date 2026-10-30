"""Order-flow imbalance risk config.

Flow-imbalance entries are short-horizon momentum reads, so
they get the house-standard leash: 2xATR stop, 2.5xATR trail,
no fixed target (the zero-cross manages the trade), 120-bar
(5-day) max hold as a backstop. Long/short symmetric.
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

# EMA(20) plus the 5-bar imbalance window, plus margin.
WARMUP = 25
