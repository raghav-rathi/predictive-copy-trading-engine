"""Liquidity-sweep risk config -- fade-the-hunt: the stop goes beyond
the sweep extreme (2.5xATR approximates the extreme on swept bars),
target 2xATR (sweeps target the opposite pool), 48-bar max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # LOOKBACK(20) + ATR(14) need ~20 bars; margin for stability
