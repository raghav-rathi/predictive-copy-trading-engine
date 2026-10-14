"""DeMarker risk config — mean-reversion trades are short-lived by design:
2xATR hard stop, no trailing, no fixed target (the DeM-based exit does the
trade management), 24-bar max hold so a non-reverting position can't sit."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40
