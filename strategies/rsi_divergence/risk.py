"""RSI(14) divergence risk config.

Divergence trades are counter-trend (regular) or late-trend
continuation (hidden) swing entries, so the stop is the standard
1.5xATR and the 2xATR chandelier trail takes over once the leg
extends. No fixed target: exits are divergence/signal-driven.
96-bar (~4-day) max hold keeps a failed reversal from tying up
capital. Both directions enabled: regular divergences fade the
exhausted leg, hidden divergences ride the continuing one.
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

WARMUP = 80  # RSI(14) + pivot confirmation spin-up, with margin
