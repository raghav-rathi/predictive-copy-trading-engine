"""Unger opening-breakout risk config -- Unger's rule is no take profit and
a stop loss: hard 1.5xATR stop, 1.5xATR chandelier trail to let breakouts
run, no target, 21-bar max hold so every trade is flat by session end."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=1.5,
    target_atr_mult=None,
    max_hold_bars=21,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 48
