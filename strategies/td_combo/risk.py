"""TD Combo risk config: 1xATR hard stop stands in for DeMark's stop below
the 13-count bar's low/high (the engine tracks stops from entry, not the
countdown extreme); no trailing (the price-flip exit manages the trade),
no fixed target, 24-bar max hold as the Combo time stop."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
