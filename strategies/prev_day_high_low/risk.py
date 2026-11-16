"""Prior UTC-day high/low breakout risk config.

The textbook stop sits just inside the broken level -- a failed
breakout that closes back inside the prior-day range is wrong, and
the stop goes 0.5xATR inside the level to absorb wick noise.  The
harness only supports an ATR-distance stop from the entry, so the
inside-the-level stop is approximated as 1.5xATR: entry is ~0.1%
past the level on a breakout close, so a 1.5xATR stop lands roughly
0.5-1xATR inside the level on 1h crypto, and is documented as an
approximation, not the literal level.  The 3xATR target is 2R vs
the 1.5xATR stop.  No chandelier trail -- a breakout either runs
or fails back inside the range, and the signal exit catches the
failure.  Max hold 24 bars (~1 day) caps a breakout that stalls;
the midnight-flat signal exit usually fires first.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,    # ~ 0.5xATR inside the broken level
    trail_atr_mult=None,  # off: exits are range/midnight-driven
    target_atr_mult=3.0,  # 2R vs the 1.5xATR stop
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 48  # 20-day range median needs 20 days; warmup covers spin-up
