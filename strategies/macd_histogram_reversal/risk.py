"""MACD histogram reversal risk config.

Histogram flips are fast momentum-turn signals, so the trade
is given a short leash: 2xATR stop, 2xATR trail, no fixed
target (the opposite flip manages the trade), 72-bar (3-day)
max hold — a flip that hasn't paid in three days was noise.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 50  # MACD(26) + signal(9) headroom, with margin
