"""Fakey risk config.

A fakey is a reversal off a failed break: the entry is taken
because the break was fake, so there is no take-profit target —
the exit is the opposite fakey, i.e. the range genuinely breaking
the other way. The 2xATR hard stop covers the classic failure:
the "false" break turns out to be real after all (the close back
inside was a pause, not a rejection) and price runs through the
mother bar's far side. The 3xATR chandelier trail protects the
runners without a fixed target. The 60-bar max hold keeps a
position from camping through a range where inside bars and
fakeys fire repeatedly on noise.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 5  # the pattern needs only 3 bars (mother + inside + break), with margin
