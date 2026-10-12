"""Funding Squeeze Reversal risk config -- author's spec: 12-bar max hold
(average hold in the author's BNB backtest was ~10h), hard 2xATR stop,
3xATR chandelier trailing, no fixed target (the reversing exit and the
12-bar cap do the trade management), 1% risk/trade, both sides."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=12,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 96
