"""Mass Index risk.

Dorsey's reversal call has no built-in stop, so the exits are: 3xATR chandelier
trailing (the specified exit — a volatility-expansion reversal either snaps
back fast or the thesis is wrong), 2xATR disaster stop, opposite-bulge signal
exit, and a 72-bar max hold (~3 days on 1h) so a dead reversal doesn't tie up
capital.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80
