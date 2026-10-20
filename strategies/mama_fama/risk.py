"""Ehlers MAMA/FAMA cross risk config.

The MAMA/FAMA cross structure does the trade management (exits on the
opposite cross), so there is no trailing and no fixed target. A hard
2xATR stop covers gap/reversal shock, and a 200-bar max hold prevents a
choppy regime from camping in a dead position while MAMA oscillates
around price.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # Hilbert discriminator + period estimator spin-up
