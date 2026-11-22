"""Buyable Gap-Up risk config.

The gap bar's intraday low IS the stop in the original method
(a close below it means the gap failed), and that stop lives in
the signal layer (signals.py tracks the gap bar's low/high).
The harness still needs a stop, so 2xATR(14) is the backstop for
the rare case where price gaps through the signal level without
a close below it first. No trail (the method exits on the gap
failure or the 10-day violation, not on a trail) and no target.
The 240-bar (~10-day) max hold fits the original's multi-week
ride: a gap-up that has not run in ten days was not a BGU.
1% risk per trade, 3x leverage cap. Long/short symmetric (short
mirror is builder-added).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# 1,200-bar volume average + margin.
WARMUP = 1250
