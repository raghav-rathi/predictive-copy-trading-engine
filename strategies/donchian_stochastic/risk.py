"""Donchian Stochastic risk config.

The Turtle 10-bar channel / %K-%D cross exit is the primary
exit, so the harness 2xATR hard stop / 3xATR chandelier
trail sit behind it as a safety net for gap-through-channel
moves (the breakout is only recognised at the close). No
take-profit target — the trade rides the breakout until the
10-bar channel or the Stochastic turns against it. The
120-bar max hold is the Turtle-scale cap: a breakout that
has not resolved in five days is not the trend this system
is built to ride.

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
