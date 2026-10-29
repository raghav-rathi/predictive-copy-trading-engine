"""Stochastic Pop risk config.

Pops are momentum bursts that either extend immediately or fail:
a tight 1.5xATR stop, 2xATR trail, 3xATR target, and a short
72-bar (3-day) max hold -- a pop that has not extended in three
days was not a pop. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=3.0,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # fastK(14) + prior 20-bar range, with margin
