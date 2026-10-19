"""Harmonic Gartley risk config -- pattern-completion reversal system:
2xATR hard stop (executable proxy for the classical stop-beyond-X, which
the harness cannot express -- see BACKTEST.md), 4xATR take-profit target
(patterns aim for outsized moves off the PRZ), no trailing, 100-bar max
hold so stale patterns don't camp."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=4.0,
    max_hold_bars=100,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
