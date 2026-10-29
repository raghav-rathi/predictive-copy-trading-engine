"""Counterattack lines risk config.

Counterattack lines are a weak reversal signal (Nison ranks them
below piercing/dark-cloud), so the stop is roomy (2xATR) and the
trail is 2.5xATR; no fixed target (the opposite-counterattack
exit manages the trade). 72-bar (3-day) max hold: a bridled
trend that has not turned in three days was just a pause.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 20  # ATR(14) plus margin; the pattern itself needs 7 bars
