"""ADX + MACD trend risk config (batch standard).

Trend trades need room to breathe, so the stop is 2xATR with a
2.5xATR chandelier trail and no fixed target — the opposite-MACD /
ADX-fade signal exits do the trade management. The 168-bar (~7-day)
max hold caps a stale trend trade. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # ADX/MACD spin-up (26-bar slow EMA + 9-bar signal) + margin
