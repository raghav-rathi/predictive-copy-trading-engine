"""Traders Dynamic Index risk config.

The price/signal cross is the exit logic, so the harness
2xATR hard stop / 3xATR chandelier trail sit behind it as a
safety net for gap-through-cross moves. No take-profit
target — the trade rides the TDI cross until the opposite
cross. The 60-bar max hold keeps a position from camping
through sideways cross chop.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # RSI(13) + SMA(34) spin-up, with margin
