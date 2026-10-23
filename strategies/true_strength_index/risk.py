"""True Strength Index cross system risk config.

TSI cross trades are medium-horizon momentum swings: the entry needs
both a signal-line cross and agreement with the momentum territory, so
the stop is 1.5xATR (a failed cross reverses fast — don't linger) with
a 2xATR chandelier trail taking over once the leg extends. No fixed
target: exits are the opposite signal-line cross. 120-bar (~5 day) max
hold frees capital from dead legs. Both sides allowed: the oscillator
is symmetric by construction.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120  # double-EMA(25,13) + EMA(7) spin-up, with margin
