"""Wilder DMI risk.

The Parabolic SAR flip is the trailing mechanism (emitted as a signal exit),
so no ATR trailing is configured. The 2xATR hard stop is disaster protection
against gaps that jump the SAR without printing through it. 120-bar max hold
(~5 days on 1h) bounds capital in DI whipsaws that never resolve into a SAR
flip; the ADX<20 / range-rule exits usually fire first.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
