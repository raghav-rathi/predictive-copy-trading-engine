"""Multi-timeframe stack risk config (standard batch risk layer)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# 4h EMA(50) needs 50 completed 4h bars = 200 1h bars, plus the
# 1h EMA(21) lookback and margin: 200 + 21 + 9 = 230.
WARMUP = 230
