"""Heikin Ashi + Stochastic risk config.

The signal exit is the opposite %K/%D cross, so the harness
2xATR(14) stop / 3xATR(14) chandelier trail sit behind it as
a safety net for gap-through-cross moves (the cross is only
recognised at the close, so an adverse gap can run past it).
The 60-bar max hold keeps a position from camping through a
flat stochastic range. No take-profit target — the trade
rides the HA trend until the stochastic cross rolls over.
1% risk per trade, 3x leverage cap. Long/short symmetric.
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

# EMA(50) on ha_close + stochastic 14-bar window, with margin.
WARMUP = 60
