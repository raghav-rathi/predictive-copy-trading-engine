"""Donchian Turtle Breakout (System 1) risk config.

The original Turtles sized by volatility (2xATR stop, N = ATR(20))
and exited on the 10-day Donchian channel; that exit lives in the
signal layer. The harness stop is the same 2xATR(20) the Turtles
used. No trail, no target — the system rides the trend until the
10-bar channel exit or the stop. Max hold 336 bars (~14 days on
1h) caps a position that never triggers either exit. 1% risk per
trade, 3x leverage cap. Long/short symmetric (System 1 trades
both directions).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=20,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=336,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# 20-bar entry channel + 20-bar ATR, with margin.
WARMUP = 60
