"""Laguerre filter trend risk config.

The Laguerre filter tracks price closely, so crosses come faster
than a 20/40 MA pair — but the 200-bar max hold is kept (same
template as the other trend engines) so winning legs are not cut
short by a fixed clock; the 3xATR chandelier trail does the lifting
and the 2xATR hard stop handles the failure case. No fixed target —
exits are cross-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # Laguerre state settles within tens of bars; margin included
