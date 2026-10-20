"""VPIN toxicity-exhaustion risk config.

The signal side defines entries only; trade management is the
risk-config's job: a symmetric 2xATR stop and 2xATR target with a
48-bar max hold. No trailing — exhaustion fades are mean-reversion
trades and a chandelier would cut the snap-back too early; the fixed
target locks in the fade instead.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# VPIN needs ~50 completed volume buckets to form (~50-70 bars given
# bucket size ~= 1h trailing volume) and the percentile rank needs 252
# trailing VPIN values; 320 bars keeps the percentile well-formed
# before any entry is allowed.
WARMUP = 320
