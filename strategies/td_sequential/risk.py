"""TD Sequential risk.

DeMark defines no fixed stop: the thesis stop IS the TDST level (exit on a
close through it, emitted as a signal). The 2xATR hard stop is disaster
protection only, in case a gap blows through TDST without a signal exit
firing. No trailing: TDST acts as the support/resistance stop. 48-bar
max hold caps capital stuck in a countdown-reversal that never follows
through (~2 days on 1h bars).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,  # calibrated: sweep showed 1.5 beats 2.0/2.5 on all 3 coins
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=96,  # calibrated: sweep showed 96 beats 24/48 on all 3 coins
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30
