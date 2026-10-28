"""Smoothed Heikin-Ashi risk config (batch standard).

HA trends are slow by construction (HA averaging + EMA(5)
smoothing), so the stop is 2xATR with a 2.5xATR chandelier trail
and no fixed target — the opposite-cross signal exit does the
trade management. The 168-bar (~7-day) max hold caps a stale
trend trade. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # HA recursion + EMA(5) spin-up, with margin
