"""Bollinger %B risk config.

%B band-tag trades are mean-reversion entries: the stop is a
standard 1.5xATR (a tag that keeps running past the band was not a
tag, it was a breakout), the 2xATR chandelier trail locks in the
legs that extend to the mid-band and beyond, and there is no fixed
target — the 0.5 mid-band cross is the exit. The 72-bar (~3-day)
max hold fits the thesis: a band tag that hasn't reverted in three
days is a trend, not a tag. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 50  # BB(20) + ATR(14) spin-up, with margin
