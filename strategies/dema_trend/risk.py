"""DEMA Trend Cross risk config.

DEMA crosses are faster than plain-EMA crosses (that is the point of
Mulloy's construction), so trades catch trend legs early but are also
more exposed to chop. The 2xATR hard stop keeps failed breaks small,
the 2.5xATR chandelier trail rides genuine legs, and the 200-bar max
hold (200 1h bars ~= 8.3 days) caps a stale trend-follow from drifting
sideways indefinitely. No fixed target — exits are cross-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 140  # DEMA(55) spin-up ~2*(55-1) = 108 bars, with margin
