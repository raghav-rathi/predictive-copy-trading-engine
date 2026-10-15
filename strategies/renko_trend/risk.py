"""Renko trend risk config — brick reversals are the whole system:
hard 2xATR stop beyond the noise the bricks already filtered, the
opposite brick flip manages exits, no fixed target, 200-bar max hold
for long brick trends."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40
