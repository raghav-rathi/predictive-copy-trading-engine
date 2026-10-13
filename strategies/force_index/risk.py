"""Force Index risk: 2.5xATR(14) hard stop (Elder-style disaster protection
for a fast pullback system); signal exits (FI13 flip, FI2 hook) carry the
trade management, so no chandelier trailing and no fixed target. 168-bar
(7-day) max hold is hygiene for pullback entries that go stale in chop."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# EMA(13) + ATR(14) settle + a few FI2 hook bars.
WARMUP = 48
