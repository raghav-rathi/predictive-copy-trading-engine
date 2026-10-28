"""Pennant pattern risk config (batch standard).

Breakout trades need room past the range, so the stop is 2xATR
with a 2.5xATR chandelier trail and no fixed target — the
opposite-breakout signal exit and the max hold do the trade
management. The 168-bar (~7-day) max hold caps a breakout that
goes nowhere. Long/short symmetric.
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

WARMUP = 40  # pole + consolidation + volume average spin-up, with margin
