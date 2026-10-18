"""Elder Impulse System risk config -- Elder's own style is a tight stop under
the bar extreme; here a 1.5xATR hard stop, no trailing (the color-flip exit
does the trade management), no fixed target, 48-bar max hold."""

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
