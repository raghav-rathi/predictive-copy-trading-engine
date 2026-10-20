"""ALMA dual-cross risk config.

The cross + breakout structure does the trade management (exits on the
opposite cross), so there is no trailing and no fixed target — the 2xATR
hard stop covers gap/reversal shock, and a 200-bar max hold prevents a
post-breakout chop regime from camping in a dead position. Breakout
entries can run multi-day trends, hence the long 200-bar allowance.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # ALMA(21) + 20-bar breakout spin-up, with margin
