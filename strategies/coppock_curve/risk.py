"""Coppock risk config -- slow-regime posture: 2xATR hard stop, 3xATR
chandelier trail, 720-bar (30-day) max hold so slow zero-cross regimes
can play out, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=720,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # ROC(14) + WMA(10) needs 24 bars; margin for stability
