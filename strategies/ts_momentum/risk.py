"""Time-series momentum risk config.

3xATR hard stop, no chandelier trailing and no fixed target — exits come
from the hysteresis rule (both ratios decaying past +/-0.3). max_hold_bars
= 672 (4 weeks) caps stale positions; 1% risk per trade, 3x leverage cap."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=3.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=672,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 750
