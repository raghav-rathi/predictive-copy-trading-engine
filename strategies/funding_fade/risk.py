"""Negative-funding fade risk config.

The source (Jlabs) holds a fixed 8 hours with no stop and no target
— the edge is the funding regime, not a price level. The house
harness still needs a catastrophic backstop, so the stop is a roomy
2xATR (wide enough that the 8h hold, not the stop, normally decides
the trade) with no trail and no target; the 8-bar max hold is the
real exit and matches the signal-level 8-bar exit. Long only.

Deviation from source, documented: Jlabs' backtest has no stop-loss;
the 2xATR stop is a risk overlay, not part of the published model,
and it can only cut trades short, never extend them.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=8,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 24  # one day of funding history so the turn test is meaningful
