"""Spinning top risk config.

The spinning top is an exhaustion/reversal signal at a swing
extreme, so the trade is a counter-trend reversal with the
extreme itself as the natural invalidation: a long entered at
a swing low is wrong if price makes a clean new low, a short
at a swing high is wrong on a clean new high. The 2xATR hard
stop covers that failure (the "exhaustion" was just a pause
inside a continuing move). The 3xATR chandelier trail lets a
genuine reversal run. There is no take-profit target — the
exit is the opposite signal (a spinning top at the opposite
extreme). The 60-bar max hold keeps a position from camping
through chop where tops print repeatedly at no extreme.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # 20-bar swing window plus spin-up, with margin
