"""RSI pullback to EMA(50) risk config.

2xATR(14) harness stop as a backstop (the signal exits — RSI
70/30 or the EMA(50) break — are the real exits). No trail
(the exit is the RSI round-trip, not a trailing stop) and no
target. Max hold 120 bars (~5 days): a pullback bounce that
has not reached RSI 70 in five days was not a bounce. 1% risk
per trade, 3x leverage cap. Long/short symmetric.
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

# EMA(50) needs 50 bars to exist; 60 bars of margin.
WARMUP = 60
