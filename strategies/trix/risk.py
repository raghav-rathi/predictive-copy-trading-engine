"""TRIX risk config.

TRIX is a slow triple-smoothed oscillator: positions need room to let
a confirmed momentum turn develop, so the max hold is long (200 bars,
~8 days) and the 3xATR chandelier trail does the lifting once a leg
extends. The 2xATR hard stop handles the failure case — a turn-up that
rolls back over is usually a quick reversal, so a tight stop keeps
those losers small. No fixed target — TRIX exits are cross-driven.
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

WARMUP = 80  # triple-EMA(14) spin-up (~39 bars) + signal EMA(9), with margin
