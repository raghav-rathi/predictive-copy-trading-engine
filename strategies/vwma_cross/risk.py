"""VWMA-cross risk config -- volume-confirmed trend posture:
2xATR hard stop, 3xATR chandelier trail, 120-bar max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # VWMA(50) needs 50 bars; margin for stability
