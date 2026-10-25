"""Flag breakout risk config.

Flags are short, fast patterns: the tighter house variant — 1.5xATR
stop, 2xATR trail, 72-bar (3-day) max hold. A flag breakout that
hasn't run in three days is a failed flag. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # pole + consolidation spin-up, with margin
