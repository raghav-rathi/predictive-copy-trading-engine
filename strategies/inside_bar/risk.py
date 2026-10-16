"""Inside-bar breakout risk config — the published version stops beyond the
mother-bar extreme; this harness approximates that with 2xATR hard stops
and 4xATR targets (~2R), 48-bar max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=4.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
