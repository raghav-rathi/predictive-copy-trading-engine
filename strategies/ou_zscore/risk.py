"""OU half-life z-score mean-reversion risk config.

Mean-reversion trades get room: a 2.5xATR hard stop (the deviation can
stretch further before it snaps back), no fixed target and no
trailing — the signal exit (z back to 0) defines the trade. A 200-bar
max hold caps exposure when the regime shifts and the half-life
estimate goes stale.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# AR(1) fit needs 100 trailing dev values and the dev itself needs a
# 50-bar SMA; 120 bars leaves the rolling std well-formed before any
# entry is allowed.
WARMUP = 120
