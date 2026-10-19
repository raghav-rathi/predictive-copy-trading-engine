"""CVD divergence risk config -- divergence-reversal system: a wide 4xATR
hard stop used for sizing only (the catastrophe backstop), a 3xATR
chandelier trailing stop as the primary trade manager, no fixed target
(divergence trades have no natural measured move), no max hold (the
trailing stop or the opposite divergence gets the trade out), 1% risk
per trade."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=4.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100
