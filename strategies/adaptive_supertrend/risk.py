"""Adaptive Supertrend risk config.

Supertrend is a trend-following flip system: positions need room to
let a leg develop, so the max hold is 200 bars (~8 days) and the
3xATR chandelier trail does the lifting once a leg extends. The 2xATR
hard stop handles the failure case -- a flip that immediately rolls
back is usually a whipsaw, so a tight stop keeps those losers small.
No fixed target -- exits are flip-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # ATR(10) + Choppiness(14) spin-up, with margin
