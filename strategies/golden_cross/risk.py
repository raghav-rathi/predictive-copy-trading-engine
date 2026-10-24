"""Golden Cross / Death Cross risk config.

A 50/200 cross is a slow regime signal: the stop is 2.0xATR
(a regime trade needs room — a 1.5xATR stop would be shaken out
by the same chop the cross filters out) and the trail is a wide
3.0xATR chandelier to ride the regime leg, with no fixed target
— the opposite cross is the exit. The 240-bar (~10-day) max hold
fits the thesis: a cross that hasn't paid within ten days on 1h
bars is a failed regime call, not a slow winner. Long/short
symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 250  # SMA(200) spin-up, with margin
