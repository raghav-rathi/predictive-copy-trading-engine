"""Premium/discount risk config.

The equilibrium cross is both entry trigger and exit: the trade
is a reclaim of the range midpoint after a sweep of one extreme,
so losing the midpoint again invalidates it outright. There is
no take-profit target — a reclaim that holds can run to the
opposite extreme of the range and beyond. The 2xATR hard stop
covers the classic failure: the sweep was not a sweep but the
start of a genuine range break, and price keeps going. The
3xATR chandelier trail protects the runners without a fixed
target. The 60-bar max hold keeps a position from camping
through sideways equilibrium chop where crosses fire repeatedly
on no follow-through.
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

WARMUP = 60  # 48-bar range spin-up plus the 12-bar touch window, with margin
