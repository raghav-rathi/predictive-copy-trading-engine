"""Engulfing-reversal risk config.

Engulfing entries are short-horizon reversal trades: the 1.5xATR stop
caps the loss if the "reversal" was a false print, the 2xATR
chandelier trail locks in the occasional strong leg, and no fixed
target lets the pattern's own negation (an opposite engulfing, via
the signal exit) do the exiting work. 48-bar (~2 day) max hold keeps
a dead reversal from tying up capital. Both directions allowed
(allow_longs + allow_shorts) — the pattern is symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # EMA(20) + ATR(14) spin-up, with margin
