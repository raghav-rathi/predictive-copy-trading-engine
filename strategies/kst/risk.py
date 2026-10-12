"""KST risk config -- broad-momentum posture: 2xATR hard stop, 3xATR
chandelier trail, 120-bar (5-day) max hold, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 90  # ROC(30)+SMA(15) needs 45 bars; signal adds 9
