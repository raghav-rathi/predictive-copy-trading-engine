"""Gator Oscillator risk config.

Gator entries ride Alligator expansions, which develop over multi-day
trends: positions get room with a 150-bar (~6 day) max hold and a
3xATR chandelier trail that does the lifting once a leg extends. The
2xATR hard stop handles the failure case — an expansion that dies
immediately usually means the mouth snapped shut, and those losers
should be small. No fixed target — Gator exits are state-driven
(sleeps / fan flip).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # SMMA(13) spin-up (13 bars) + 8-bar jaw displacement, with margin
