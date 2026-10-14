"""Awesome Oscillator risk config -- Williams-style: hard 2xATR stop,
no trailing (the zero-line cross exit does the trade management), no
fixed target, 72-bar max hold to keep AO drift trades from camping."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 70
