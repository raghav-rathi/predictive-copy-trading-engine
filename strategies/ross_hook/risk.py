"""Ross Hook risk config.

Continuation entries after a completed 1-2-3 + breakout + hook have a
natural invalidation (back through P1 / hook failure), approximated by
the harness's 1.5xATR stop. No trail: the edge is the breakout leg,
not a long trend. 2.5xATR target ~= the measured 1-2-3 swing
projection. 60-bar max hold keeps a stalled breakout from camping.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.5,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # pivots need 2*side+1 bars; sequences need room to form
