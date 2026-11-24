"""Ichimoku + Stochastic risk config.

The entry is a trend-plus-momentum-reversal hybrid (price above
the cloud with a Stochastic turn up from oversold), so the stop
is the standard 2xATR(14) and the exit is the opposite
Stochastic cross or a close back into the cloud. A 3xATR
chandelier trail protects open profit on the trend leg, and a
120-bar (~5-day) max hold caps a position whose exit conditions
never fire. 1% risk per trade, 3x leverage cap. Long/short
symmetric.
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

# Senkou B needs 52 bars + 26-bar shift = 78 bars before the
# cloud is formed, plus margin.
WARMUP = 80
