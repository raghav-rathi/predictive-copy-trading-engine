"""Keltner Channel + MACD combo risk config.

The channel break is the entry and the close back inside the
channel (or the histogram flipping sign) is the exit, so the
signal layer carries the real exit. The harness stop is a
2xATR(14) backstop for gap-through moves. No trail (the method
exits on the channel re-entry, not on a trail) and no target.
The 120-bar (~5-day) max hold fits a channel-breakout ride: a
breakout that has not run in five days was not a breakout.
1% risk per trade, 3x leverage cap. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# MACD(12,26,9) signal/histogram needs ~34 bars to seed; 40 bars
# of margin covers the Keltner EMA(20) as well.
WARMUP = 40
