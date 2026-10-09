"""ORB risk: the original's 8:1 (32-tick TP / 4-tick SL) becomes 3xATR
target / 1xATR stop on 1h crypto. 20-bar max hold keeps it intraday."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.0,
    trail_atr_mult=None,
    target_atr_mult=3.0,
    max_hold_bars=20,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30
