"""Schwager volatility-ratio risk config.

The textbook stop sits just beyond the wide bar's extreme (above the
wide bar's high for a short fade, below its low for a long fade): a
move past it means the bar was continuation, not exhaustion.  The
harness only supports an ATR-distance stop, so the wide-bar-extreme
stop is approximated as 2xATR -- a wide bar is by definition ~2x its
recent true-range norm, so 2xATR from the next-bar entry lands just
past the bar's extreme in the usual case, and is documented as an
approximation, not the literal bar extreme.  The 3xATR target is
1.5R vs the 2xATR stop.  No chandelier trail -- a 10-bar fade has no
room for a trail to do anything but choke it.  Max hold 10 bars is
the time exit: a fade that has not worked in 10 hours is wrong.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,    # ~ just beyond the wide bar's extreme
    trail_atr_mult=None,  # off: 10-bar fade, no trail
    target_atr_mult=3.0,  # 1.5R vs the 2xATR stop
    max_hold_bars=10,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # VR EMA(14) spin-up + 5-bar return, plus margin
