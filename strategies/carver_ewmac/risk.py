"""Rob Carver EWMAC risk config -- trend-following system: hard 2xATR stop,
no trailing (the forecast-band exit manages the trade), no fixed target
(Carver scales position by forecast strength; the harness sizes a fixed
1% risk per trade instead -- see CALIBRATION.md), 120-bar max hold to
keep dead trends from camping."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 300
