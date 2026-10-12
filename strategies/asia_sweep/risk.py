"""Asia Sweep risk config.

Spec: SL = sweep extreme -/+ 0.5xATR, TP = 3R, 1% risk/trade, max 1
concurrent, flat at 20:00 UTC. The event-driven harness anchors the hard
stop at entry +/- stop_atr_mult x ATR(14) and the target at
target_atr_mult x ATR(14); the shipped 1.0xATR stop / 3.0xATR target is
the harness-anchored approximation of the spec's sweep-extreme SL with
3R TP (calibration confirms 1.0x is not a knife edge — see
CALIBRATION.md). No trailing; 24-bar max hold is a backstop behind the
20:00 UTC flat. Both sides; the harness is one-position-at-a-time, which
matches the spec's max-1-concurrent rule.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.0,
    trail_atr_mult=None,
    target_atr_mult=3.0,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
