"""OBV divergence risk config.

Divergence entries are counter-trend: the position bets on a reversal
that has only just been hinted at, so the hard stop is tight (1.5xATR)
— if the swing continues past the pivot, the thesis is wrong. The
2.5xATR chandelier trail lets a genuine reversal run once it proves
itself. No fixed target: the exit rule (opposite pivot print) is the
target. max_hold_bars=60 caps a position through ~2.5 days of drift
after the pivot; divergences either resolve fast or fail, so camping
is pointless.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # pivot_k=10 lag on both ends + OBV/ATR spin-up, with margin
