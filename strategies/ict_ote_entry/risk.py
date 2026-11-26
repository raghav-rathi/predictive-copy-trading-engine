"""ICT Optimal Trade Entry (OTE) risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail, no
take-profit target, 120-bar max hold, 1% risk/trade, 3x
leverage cap.

Deviation from ICT, documented: ICT places the stop beyond
the leg start (the sweep extreme, i.e. beyond 100% of the
leg). Here the house 2xATR stop replaces that structural
stop -- the sweep extreme is still used, but only as the
signal exit (a close beyond it exits the trade) and as the
pending-setup invalidation, not as the stop level.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # swing(20) + ATR(14) + state-machine spin-up, with margin
