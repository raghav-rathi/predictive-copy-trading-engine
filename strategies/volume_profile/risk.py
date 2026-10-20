"""Volume profile value-area fade risk config.

Fades at the value-area edges are meant to travel back across the
value area: a 2xATR hard stop and a 3xATR target (a proxy for the full
VAL->VAH rotation) with a 120-bar max hold. No trailing — the trade
thesis is the rotation, not a trend extension.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=3.0,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# The rolling profile needs 168 bars to form; 200 bars of warmup leaves
# VAL/VAH well-established before any entry is allowed.
WARMUP = 200
