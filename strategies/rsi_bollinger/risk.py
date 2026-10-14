"""Bollinger-on-RSI risk config -- mean-reversion posture: tight 1.5xATR
hard stop (fading extremes), no trailing (exits are signal-driven),
48-bar (2-day) max hold so stale mean-reversion bets die, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 50  # RSI(14) + 20-bar bands needs 34 bars; margin
