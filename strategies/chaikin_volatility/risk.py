"""Chaikin Volatility risk config.

Volatility-expansion entries are, by construction, taken into a
moment of elevated range: positions must survive the expansion itself
so they can ride the directional leg that follows, but they must not
sit through the reversal that often comes next. The 2xATR hard stop
absorbs the expansion spikes; the 1.5xATR chandelier trail tightens
behind price once a leg extends (closer than the default 3x trail,
because range-expansion legs reverse harder); the 100-bar max hold
(~4 days) keeps the engine out of dead drift; exits are otherwise
driven by cv rolling back over (see signals.py). No fixed target —
volatility spikes have no price target to give.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=1.5,
    target_atr_mult=None,
    max_hold_bars=100,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 70  # cv(10,10) valid after ~19 bars, sma50 after 50, with margin
