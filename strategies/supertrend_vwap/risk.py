"""Supertrend VWAP risk config.

The Supertrend flip / VWAP cross exit is the primary exit,
so the harness 2xATR hard stop / 3xATR chandelier trail sit
behind it as a safety net for gap-through moves (the flip
is only recognised at the close). No take-profit target —
the trade rides the agreed trend until either leg turns
against it. The 120-bar max hold caps a trend that has not
resolved in five days.

The harness 2xATR hard stop / 3xATR chandelier trail sit behind
the strategy exit as a safety net for gap-through moves. No
take-profit target. The 120-bar max hold caps a trade that has
not resolved in five days.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40
