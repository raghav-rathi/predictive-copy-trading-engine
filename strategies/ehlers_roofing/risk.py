"""Ehlers Roofing Filter risk config.

Zero-cross entries are cycle-turn trades: the roofing line turns
fast, so the stop is a standard 1.5xATR with a 2xATR chandelier
trail to ride the cycle leg that extends, and no fixed target —
the opposite zero cross is the exit. The 72-bar (~3-day) max hold
covers ~1.5 tuned cycles: a cycle turn that hasn't resolved in that
time was not a cycle turn. Long/short symmetric.
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

WARMUP = 80  # high-pass + SuperSmoother spin-up (48-bar cycle) + margin
