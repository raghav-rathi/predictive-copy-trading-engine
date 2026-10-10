"""Chandelier Exit risk config.

The chandelier line IS the trailing exit, so the risk layer only carries
a 2xATR(14) safety stop (catastrophe protection against gap-through-stop
where the chandelier never prints), no fixed target, no max hold: a trend
system lets the chandelier decide when the trade is over.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
