"""Holy Grail risk.

Raschke's stop IS the swing low/high formed by the pullback — emitted as a
signal exit. The 2xATR hard stop is disaster protection only (gap through the
swing level without a close below it registering first is rare on 1h, but the
belt-and-braces stop costs little). No trailing: the ADX<25 exit plus the
swing stop define the trade. 72-bar max hold (~3 days on 1h) frees capital
from pullbacks that never trigger follow-through.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
