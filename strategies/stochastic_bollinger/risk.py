"""Stochastic + Bollinger %b risk config.

Mean reversion into the band: the trade is a return toward the
mid-band, so the stop is the 2xATR(14) harness backstop and the
signal-level exit (%b reaching the opposite band, or %K rolling
over) is the real exit. No trail (a trail would fight the
mean-reversion exit) and no target (the opposite band IS the
target, enforced in signals.py). 120-bar (~5-day) max hold: a
reversion that has not happened in five days was not a reversion.
1% risk per trade, 3x leverage cap. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# Bollinger(20) + Stochastic(14,3,3) need 20 bars; margin for the
# 3-bar smoothings and the cross to form.
WARMUP = 40
