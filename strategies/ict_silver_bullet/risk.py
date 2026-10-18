"""ICT Silver Bullet risk config.

The textbook stop sits beyond the FVG extreme with a 2R target; the
harness works in ATR multiples, so the FVG-extreme distance is
approximated with stop_atr_mult=0.75 and the 2R target with
target_atr_mult=1.5 (2x the stop distance). No trailing -- the
killzone trade is a session scalp -- and max_hold_bars=24 forces the
exit by the next session."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=0.75,
    trail_atr_mult=None,
    target_atr_mult=1.5,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 220
