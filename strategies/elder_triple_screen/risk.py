"""Triple Screen risk config.

Elder's exits are screen-driven: the position dies when the 6h trend
screen flips, so no fixed take-profit -- the trail is the workhorse for
locking in multi-day tide rides. The 6h MACD histogram is slow, so the
trend can run a long way before flipping; the 3.5xATR chandelier keeps
the strategy in those runs while the 2.5xATR hard stop covers the
occasional sharp counter-tide gap. A 150-bar max hold (~6 days) caps
the damage when the trend screen goes flat-ish and neither the exit
nor the trail fires for a long stretch.

WARMUP=200: the 6h MACD(12,26,9) needs ~26 6h bars (~156 1h bars) to
spin up, plus margin for the histogram slope comparison and the 1h
Force Index warmup.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=3.5,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 200
