"""Keltner mean-reversion risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail, no
take-profit target, 1% risk/trade, 3x leverage cap. The
72-bar max hold (3 days on 1h bars) bounds a fade that
never mean-reverts to the midline; a band tag that has not
reverted within three days is not the setup.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # EMA(20) + ATR(10) + margin
