"""NR7 risk config -- Crabel-style breakout: 1.5xATR stop from entry (the
opposite NR7 extreme acts as the natural stop; the ATR stop adds a guard
for gap-through cases), no trailing and no fixed target (breakouts are
asymmetric and the reverse-break exit does the trade management), 24-bar
max hold to avoid sitting in failed breakouts."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30
