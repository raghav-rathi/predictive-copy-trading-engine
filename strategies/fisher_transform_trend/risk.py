"""Fisher Transform trend risk config.

The Fisher 0-cross is the entry/exit trigger and the two-bar
turn is the signal-level exit, so the harness stop is a backstop
only: 2xATR(14). No trail, no target — the method rides the
Fisher trend until it crosses back or turns. 120-bar (~5-day)
max hold caps a stale trend ride. 1% risk per trade, 3x
leverage cap. Long/short symmetric.
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

# 10-bar Fisher window + smoothing settle + margin.
WARMUP = 30
