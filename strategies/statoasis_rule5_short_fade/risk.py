"""StatOasis Rule 5 risk config.

Rule 5 is a 5-bar fade: enter the double-overbought short and be
out 5 bars later, win or lose. The stop is a roomy 2xATR so the
fixed hold, not the stop, normally ends the trade; no trailing
stop (a trail would fight the fixed-hold thesis) and no target.
max_hold_bars=5 mirrors the signal-level hold as a harness
backstop. 1% risk per trade, 3x leverage cap. Long/short
symmetric (long mirror is builder-added).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=5,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# SMA(100) + margin.
WARMUP = 120
