"""Tillson T3 risk config.

The signal layer exits on a close back through T3(10) or on
T3(10) turning against the position, so the harness stop is a
backstop only: 2xATR(14). No trail (the T3 itself is the
trailing mechanism — it turns fast by design) and no target.
The 168-bar (~7-day) max hold caps how long a trend ride can
linger after the T3 has gone flat. 1% risk per trade, 3x
leverage cap. Long/short symmetric.
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

# Six stacked EMAs of period 30 need ~2-3 periods to settle; 60 bars.
WARMUP = 60
