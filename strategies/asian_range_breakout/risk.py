"""Asian-range breakout risk config.

One-day window: the time exit at 16:00 UTC is the primary
exit, with a 24-bar max hold as the backstop (one full day of
1h bars). Otherwise the house standard: 2xATR stop, 2.5xATR
trail, no fixed target, 1% risk, 3x leverage cap.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 25  # 20-bar volume average plus margin
