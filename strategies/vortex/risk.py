"""Vortex risk: trend-following cross system; the opposite cross is the
exit. Hard 2.5xATR disaster stop (per published guidance); no trailing
(the cross itself is the trailing logic). No target, no max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # VI(14) + ADX(14) need ~3x period to stabilize
