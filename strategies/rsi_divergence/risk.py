"""RSI divergence risk config — divergence entries are counter-trend
by construction, so the stop is tighter (1.5xATR) while a 2.5xATR
chandelier trail lets the reversal leg run if it catches; 72-bar
max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
