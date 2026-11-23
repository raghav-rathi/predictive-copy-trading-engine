"""Wilder ADX/DMI trend-system risk config.

The opposite DI cross (or ADX falling below 20) is the exit, so
the signal layer carries the real exit. The harness stop is a
2xATR(14) backstop for gap-through moves. No trail (Wilder's
system exits on the cross / trend failure, not on a trail) and
no target. The 168-bar (~7-day) max hold fits a Wilder trend
ride: a trend that has not run in a week on 1h bars was not a
trend. 1% risk per trade, 3x leverage cap. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# ADX(14) needs ~14 bars to seed the DIs plus smoothing time for
# DX/ADX; 40 bars of margin covers it.
WARMUP = 40
