"""Coppock Curve risk config.

The Coppock Curve is a slow indicator — a signal can take weeks
to develop on 1h bars — so the max hold is 240 bars (10 days),
long enough for a monthly-scale hook to play out. The 2xATR hard
stop / 3xATR chandelier trail sit behind the signal exits as a
safety net for gap-through moves. No take-profit target — the
trade rides until the curve turns against it or crosses zero.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 600  # ROC(336) + WMA(240) spin-up, with margin
