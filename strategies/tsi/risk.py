"""TSI risk: momentum-cross system; opposite cross is the exit.
2.5xATR hard stop; max_hold 120 bars caps how long a momentum call can
stale (momentum decays). No trailing: exits are signal-driven."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 90  # double EMA(25,13) needs ~3x(r+s) to stabilize
