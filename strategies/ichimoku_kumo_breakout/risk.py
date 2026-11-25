"""Ichimoku Kumo breakout risk config.

The cloud re-entry exit is the strategy's exit logic, so the
harness 2xATR hard stop / 3xATR chandelier trail sit behind
it as a safety net for gap-through-cloud moves (the breakout
is only recognised at the close, so an adverse gap can run
past it). No take-profit target — the trade rides the cloud
breakout until price comes back into the cloud. The 120-bar
max hold is longer than the 60-bar standard because cloud
trades run longer by design.
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

WARMUP = 80  # senkou(52) + 26-bar forward shift, with margin
