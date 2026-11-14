"""Heikin Ashi delta risk config.

Heikin Ashi delta is a smoothed momentum-turn signal: entries come a
few bars after the real turn (smoothing lag), so the 2xATR hard stop
caps the late-entry failure case and the 3xATR chandelier trail does
the lifting once a leg extends. No fixed target — exits are
delta-zero-cross driven. Max hold 150 bars (~6 days).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # HA recursion needs no long spin-up; 60 bars of margin
