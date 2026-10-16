"""Ultimate Oscillator risk config — divergences are slow-burn setups:
a plain 2xATR hard stop with no trail (the UO>70 / UO<30 extremes
manage exits), 96-bar max hold to let the divergence play out."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120
