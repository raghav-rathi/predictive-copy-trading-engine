"""DPO risk config -- cycle-timing posture: 2xATR hard stop, 2.5xATR
chandelier trail, 72-bar (3-day) max hold so stale cycle reads die,
both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # SMA(21) + 11-bar displacement needs 32 bars; margin
