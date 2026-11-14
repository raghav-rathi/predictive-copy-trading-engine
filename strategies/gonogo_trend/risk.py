"""GoNoGo Trend risk config.

GoNoGo is a trend-state engine: entries mark the birth of a Go/NoGo
regime, so positions need room for the regime to pay -- 150-bar
(~6-day) max hold, 2xATR hard stop for the failed-transition case,
3xATR chandelier trail to ride a persistent Go/NoGo state. No fixed
target -- exits are state-driven (back to neutral or the opposite
state).
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

WARMUP = 80  # EMA(50) + Donchian(50) + MACD-hist z(50) spin-up, with margin
