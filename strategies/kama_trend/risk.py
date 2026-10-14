"""KAMA trend risk config -- trend-following: the mirror-cross exit in
signals.py does the trade management, so no trailing/target/max-hold; a
2.5xATR hard stop is kept as a safety net against gap-driven blowups."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
