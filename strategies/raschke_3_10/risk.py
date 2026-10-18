"""Raschke 3/10 risk config: 1.5xATR hard stop, no trailing (the
cross-back exit manages the trade), no fixed target, 48-bar max hold
to cap a stalled momentum trade at two days on 1h bars."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
