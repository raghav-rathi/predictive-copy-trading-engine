"""Vortex crossover risk config.

The Vortex cross is a fast trend-regime trigger (1h crosses typically
resolve within a few days), so exits stay cross-driven and the exits
are reinforced rather than stretched: a 2xATR hard stop covers
gap/reversal shock against the trigger, a 3xATR chandelier trail locks
in trend legs without waiting for the opposite cross, and a 120-bar
(~5 day) max hold prevents a post-cross chop regime from camping in a
dead position. No fixed target — the VI cross regime does the work.
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

WARMUP = 60  # Vortex(14) + ATR(14) spin-up, with margin
