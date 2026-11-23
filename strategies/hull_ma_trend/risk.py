"""Hull MA trend risk config.

The signal layer exits on a close back through HMA(16) or on
HMA(16) turning against the position, so the harness stop is a
backstop only: 2xATR(14). No trail (the HMA itself is the
trailing mechanism — it turns fast by design) and no target.
The 168-bar (~7-day) max hold caps how long a trend ride can
linger after the HMA has gone flat. 1% risk per trade, 3x
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

# HMA(64) is first valid at bar 71; 100 bars leaves margin.
WARMUP = 100
