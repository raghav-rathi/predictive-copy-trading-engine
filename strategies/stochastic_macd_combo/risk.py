"""Stochastic + MACD dual-confirmation risk config.

The Stochastic cross / MACD histogram flip is the strategy's
exit logic, so the harness 2xATR hard stop / 3xATR chandelier
trail sit behind it as a safety net for gap-through-signal
moves (the cross is only recognised at the close, so an
adverse gap can run past it). No take-profit target — the
trade rides the dual confirmation until it breaks. The
60-bar max hold keeps a position from camping through
sideways stochastic chop.
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

WARMUP = 40  # Stochastic(14)+%D(3) and MACD(26)+signal(9) spin-up, with margin
