"""CCI zero-cross risk config.

Zero-cross entries are with-trend continuation trades, so they
get more room than a mean-reversion trade: 2xATR stop, 3xATR
trail, no fixed target (the opposite zero cross manages the
trade), 240-bar (10-day) max hold for trend legs to develop.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # CCI(20) + SMA(50) trend filter, with margin
