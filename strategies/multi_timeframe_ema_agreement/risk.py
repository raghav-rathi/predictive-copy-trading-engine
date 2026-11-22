"""Multi-Timeframe EMA Agreement risk config.

Plain 1h trend-following risk: 2xATR(14) stop, 3xATR chandelier
trail, no fixed target — the opposite EMA cross is the signal
exit. 120-bar (~5-day) max hold caps a cross that goes nowhere.
1% risk per trade, 3x leverage cap (house standard).
Long/short symmetric.
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

# 4h EMA(21) needs 21 completed 4h bars = 84 1h bars, plus margin.
WARMUP = 120
