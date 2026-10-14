"""RSI(2) risk: mean reversion wants a tight stop and a quick target —
the edge is the snap-back, not the trend. 2xATR target, 2xATR stop,
48-bar (2-day on 1h) max hold so stale pullbacks don't linger."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 220
