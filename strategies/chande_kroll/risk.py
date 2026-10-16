"""Chande & Kroll stop risk config — the Chande-Kroll lines themselves are
the trailing stops, so the harness hard stop stays loose (6xATR) and the
strategy's own cross-of-own-line exits drive the trade. No target, no
max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=6.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80
