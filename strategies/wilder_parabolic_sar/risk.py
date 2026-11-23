"""Wilder Parabolic SAR risk config.

The SAR flip is the real exit (it lives in the signal layer),
so the harness stop is a backstop only: 2xATR(14) protects
against a gap through the SAR without a flip bar first. No
trail (the SAR itself is the trailing stop — a second trail
would fight it) and no target (Wilder's system rides the
trend until it flips). Max hold 336 bars (~14 days) caps a
stale trend that never flips. 1% risk per trade, 3x leverage
cap. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=336,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# PSAR needs only a couple of bars to seed; 20 bars of margin.
WARMUP = 20
