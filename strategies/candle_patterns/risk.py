"""Candlestick pattern risk config -- pattern-reversal posture:
1.5xATR hard stop (pattern extreme), 2xATR target, 24-bar max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 20  # ATR(14) needs 14 bars; margin for stability
