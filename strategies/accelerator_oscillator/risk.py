"""Accelerator Oscillator risk config.

AC entries are acceleration-timing trades: they fire when the driving
force is just starting to move, so losers tend to fail fast (the color
rule flips) while winners need room for the momentum leg to extend.
The 2xATR hard stop keeps the failed-timing losses small, the 2.5xATR
chandelier trail protects once a leg extends, and the 120-bar (~5 day)
max hold cuts trades whose acceleration story simply fizzles. No fixed
target -- AC exits are color-driven.
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

WARMUP = 50  # SMA(med, 34) spin-up (33 bars) + SMA(ao, 5) lag, with margin
