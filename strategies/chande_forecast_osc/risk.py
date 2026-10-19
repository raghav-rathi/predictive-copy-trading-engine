"""Chande Forecast Oscillator risk config -- mean-reversion/oscillator
system: hard 2xATR stop, no trailing and no fixed target (the signal-line
cross-back exit manages the trade), 40-bar max hold so faded oscillators
do not linger, 1% risk per trade."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=40,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40
