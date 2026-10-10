"""Connors RSI(2) pullback risk config.

Mean-reversion pullbacks are designed to resolve fast or be wrong:
2.5xATR hard stop (wider than trend systems because entries sit deep
in the pullback), NO trailing and NO fixed target (the RSI(2)>70 /
RSI(2)<30 signal exits do the trade management), and a hard 30-bar
max hold so a pullback that stops mean-reverting cannot rot."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=30,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 220
