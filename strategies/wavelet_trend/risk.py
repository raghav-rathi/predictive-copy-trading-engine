"""Wavelet-trend risk config.

The level-3 approximation is a heavily denoised trend: entries fire
only when its 5-bar slope turns, so legs are slow and the 1.5xATR
stop is the main defence against a slope turn that was just noise.
The 2.5xATR target banks the leg when the denoised trend actually
extends; max hold 72 bars (~3 days) stops the strategy riding a
stale approximation whose slope has gone flat. No trail: the
slope-flip exit is the trailing mechanism.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.5,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 64  # 64-bar DWT window spin-up
