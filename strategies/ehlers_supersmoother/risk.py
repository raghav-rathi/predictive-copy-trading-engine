"""SuperSmoother risk config.

The SuperSmoother(20) filter turns roughly with a ~5-bar lag on a
step, so legs need a few days to develop but not weeks: 150-bar max
hold (~6 days) is the middle ground between fast oscillators and
slow trend systems. The 2xATR hard stop handles the failure case --
a cross that reverses is usually a quick failure, so a tight stop
keeps those losers small -- and a 2xATR chandelier trail locks in
extended legs. No fixed target: exits are cross-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # SuperSmoother(20) settles within ~60 bars, with margin
