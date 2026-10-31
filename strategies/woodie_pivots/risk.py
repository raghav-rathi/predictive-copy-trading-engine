"""Woodie pivots risk config (standard batch risk layer)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# Two full UTC days (48 bars) are needed before a bar can carry
# prior-day levels with a defined ATR; 50 adds margin.
WARMUP = 50
