"""Jurik RSX risk config.

RSX is a slow, smooth oscillator: 50-line crosses are infrequent
and the line rarely whipsaws, so positions get a long 72-bar max
hold (~3 days) to let a regime leg develop. The 1.5xATR hard stop
bounds the failure case (a cross that immediately reverses) and
the 2xATR target banks the leg; the 80/20 exits in the signal layer
do the lifting once momentum saturates. No trailing stop — exits
are RSX-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 45  # RSX warmup (length + 1 = 15) + cascade settling margin
