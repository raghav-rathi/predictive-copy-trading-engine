"""OBV trend risk config -- trend-following spec: 2xATR hard stop, no
trailing and no fixed target (the rollover exit does the trade
management), 10-day (240-bar) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
