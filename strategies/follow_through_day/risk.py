"""Follow-Through Day risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail,
no take-profit target, 240-bar max hold (10 days -- an FTD
rally that has not resolved within ten days is not the
setup), 1% risk/trade, 3x leverage cap. Long only.
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
    allow_shorts=False,
)

WARMUP = 528  # ~22 days: 20-day correction lookback (480) + 48 bars
