"""TDI risk config -- momentum-following posture: 2xATR hard stop,
3xATR chandelier trail, 96-bar (4-day) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 70  # RSI(13) + SMA(34) + BB(34) needs 47+ bars; margin for stability
