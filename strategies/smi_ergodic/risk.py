"""SMI Ergodic oscillator crossover risk config.

Zone-gated momentum-hook trades are swing-length: the cross out of
the +/-40 zone marks a momentum turn, and the 1.5xATR hard stop
bounds the whipsaw tail (oscillator crosses in a ranging 1h market
produce many small losses). The 2xATR chandelier trail rides the
leg once the turn extends. No fixed target: exits are signal-driven
(the opposite cross is the trade's own invalidation). 96-bar (~4
day) max hold keeps a stalled hook from tying up capital. Long/short
symmetric (allow_shorts=True) — Blau's oscillator is symmetric about
zero, so overbought hooks short as legitimately as oversold hooks
go long.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120  # double-EMA(5,20) + signal(5) spin-up, with margin
