"""Fisher Transform reversal risk config — tight 2xATR hard stop (a reversal
strategy, not a trend runner: no trailing, no fixed target, exits come from
the cross-back / extreme-level signals)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
)

WARMUP = 80
