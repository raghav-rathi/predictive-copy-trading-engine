"""Bayesian changepoint risk config.

Changepoint entries are regime bets: the detector fires rarely and
the post-change mean is estimated from a short run, so the position
is given a 1.5xATR stop and a 72-bar max hold (~3 days) and no fixed
target -- the exit is the next changepoint or a mean sign flip, not
a price level. The hazard itself (0.01, mean run 100 bars) lives in
the indicator layer, not here; the stop is the defence against a
volatility-only changepoint whose mean sign was noise.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 50  # BOCD spin-up (posterior needs a run to form)
