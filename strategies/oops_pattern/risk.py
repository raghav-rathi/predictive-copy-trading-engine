"""Oops gap-reversion risk config.

Williams' Oops is an intraday pattern: the gap-day overreaction is
either satisfied quickly or it isn't a trade at all. So the position
is flat by session end -- max_hold_bars=24 on 1h bars proxies the
original's flat-by-close design. A 1.5xATR hard stop sits just outside
the noise of the reclaimed extreme; no trail, no target -- the exits
are the opposite Oops signal or the session clock running out.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
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

WARMUP = 48  # completed-session range needs 47 bars to fully form, with margin
