"""Victor Sperandeo 1-2-3 risk config.

Trader Vic's rule is a stop above point 2 with a 2R target; the
harness works in ATR multiples, so the point-2 distance is
approximated with stop_atr_mult=1.5 and the 2R target with
target_atr_mult=3.0 (2x the stop distance). No trailing -- the
opposite 1-2-3 completion reverses the trade -- and a 72-bar max
hold caps stale reversals."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=3.0,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 210
