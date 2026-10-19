"""Murrey Math risk config.

Mean-reversion off Murrey extremes: the reversal itself is the edge, so
risk is a hard 2xATR stop and an 80-bar max hold (an extreme-zone bounce
that has not reached the 4/8 pivot within ~3.3 days is a failed setup,
not a slow winner). No trailing and no fixed target -- the pivot/exit
signals manage the trade.

64-bar frame (see indicators.py): the classic Murrey octave window;
calibration sweeps 32/64/128 in CALIBRATION.md.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=80,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # 64-bar frame + touch lookback + ATR spin-up
