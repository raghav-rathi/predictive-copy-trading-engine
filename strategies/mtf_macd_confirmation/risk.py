"""Multi-timeframe MACD confirmation risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail, no
take-profit target, 168-bar max hold (one week -- a
trend-following trade that has not resolved within a week is
not the setup), 1% risk/trade, 3x leverage cap.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 200  # 1h MACD warmup + ~136 bars for the 4h MACD histogram + margin
