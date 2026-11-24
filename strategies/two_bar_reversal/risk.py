"""2-bar key reversal risk config.

A short-term reversal pattern: the setup is a single bar's
exhaustion plus one confirmation bar, so the premise is stale
fast. The 60-bar max hold caps a position at ~2.5 days — if the
reversal has not played out by then, the trade is a drift, not
the pattern. The 2xATR hard stop covers the classic failure (the
"reversal" is just a pause inside a trend that resumes), and the
3xATR chandelier trail protects the runners without a fixed
target. Exits also fire on the opposite reversal signal.
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

WARMUP = 5  # one-bar shifts only; margin for the pattern to form
