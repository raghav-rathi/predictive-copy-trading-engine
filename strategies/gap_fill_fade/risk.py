"""Gap-fill fade risk config.

Gaps on 1h crypto bars are usually small and fill (or fail)
fast, so the hold is short — 24 bars (~1 day) max. The stop
is the standard 2xATR(14). No trail, no target: the fill exit
in the signal layer is the target, and a trail would fight the
mean-reversion logic (the trade wants the snap back, not a
trend leg). 1% risk per trade, 3x leverage cap. Long/short
symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# ATR(14) seeding (14 bars) plus margin.
WARMUP = 30
