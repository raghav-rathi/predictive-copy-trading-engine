"""CVD trend risk config.

CVD slope turns are an order-flow read, not a price breakout: entries
come while flow is building, so the 2xATR hard stop caps the
flow-that-fizzles case and the 3xATR chandelier trail does the lifting
once a leg extends. No fixed target — exits are slope-reversal
driven. Max hold 150 bars (~6 days).
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

WARMUP = 80  # EMA(50) spin-up (~49 bars) + CVD EMA(20), with margin
