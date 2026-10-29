"""RSI failure-swing risk config.

Failure swings are turn signals that need room to develop: 2xATR
stop, 2.5xATR trail, no fixed target (the opposite-swing exit
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

WARMUP = 50  # RSI(14) + pivot lag + a full swing pattern, with margin
