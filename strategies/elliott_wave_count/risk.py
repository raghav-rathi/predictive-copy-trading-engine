"""Elliott wave-count risk config.

The textbook stop sits at the wave-2 extreme (the wave-2 low for a
long, the wave-2 high for a short): a move past it voids the count.
The harness only supports an ATR-distance stop, so the wave-2 stop
is approximated as 2xATR -- on 1h crypto the wave-2 extreme usually
sits ~1.5-2.5xATR below a wave-3 breakout entry, so 2xATR is the
closest fixed mapping and is documented as an approximation, not
the literal wave-2 level.  The 3xATR target approximates the 1.5R
payoff implied by the 161.8% wave-5 extension vs the 2xATR stop;
the signal exit at the actual 161.8% extension level usually fires
first.  No chandelier trail -- a trail would exit on wave-4 noise
before the wave-5 target can print.  Max hold 96 bars (~4 days)
caps a count that stalls mid-wave.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,    # ~ the wave-2 extreme (see docstring)
    trail_atr_mult=None,  # off: exits are count-driven
    target_atr_mult=3.0,  # 1.5R vs the 2xATR stop
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # pivot confirmation + several swings to form a count
