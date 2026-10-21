"""Stochastic RSI risk config.

Stochastic RSI is a mean-reversion-ish momentum trigger: %K leaving
the 20/80 zones marks exhaustion, not a multi-day trend — so there
is no take-profit target (the 50-midline signal exit harvests the
bounce leg itself) and the 60-bar max hold keeps a dead exhaustion
position from camping through a regime change. The 2xATR hard stop
absorbs the classic StochRSI failure: %K leaves oversold, price keeps
falling anyway. The 3xATR chandelier trail protects the minority of
entries that run into a real trend leg without needing a separate
target mechanism.
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

WARMUP = 60  # RSI(14) + stoch window(14) + K/D smoothing (3+3) = ~34 bars spin-up, with margin
