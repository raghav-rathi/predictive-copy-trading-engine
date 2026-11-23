"""MACD divergence risk config.

Divergence entries are counter-trend by construction (buying a
lower low), so the stop is the standard 2xATR(14) and the max
hold is short — 120 bars (~5 days on 1h): a divergence that has
not turned within five days was not a turn. No trail, no target
— the exit is the histogram zero-cross or the opposite
divergence in the signal layer. 1% risk per trade, 3x leverage
cap. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# MACD slow EMA (26) + pivot confirmation (2) + margin.
WARMUP = 60
