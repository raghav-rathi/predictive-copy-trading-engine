"""CCI extreme mean-reversion risk config.

CCI extremes are fast, snap-back entries (the stretch can
extend before it releases), so the stop is a standard 2.0xATR
with a 2.5xATR chandelier trail to lock in the legs that do
extend, and no fixed target — the zero-line cross is the exit.
The 96-bar (~4-day) max hold fits the mean-reversion thesis: a
stretch that hasn't snapped back in four days is a new regime,
not a stretch. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 50  # CCI(20) + mean-deviation spin-up, with margin
