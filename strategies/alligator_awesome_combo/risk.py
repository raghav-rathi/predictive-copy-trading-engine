"""Alligator + Awesome Oscillator risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail, no
take-profit target, 1% risk/trade, 3x leverage cap. The
120-bar max hold (5 days on 1h bars) bounds a Profitunity
trend trade that never reaches its lips/AO exit; the
Alligator is a trend-following setup, so the hold is longer
than an intraday strategy's.
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

WARMUP = 60  # AO slow SMA(34) + Alligator jaw(13) + fractal lag + margin
