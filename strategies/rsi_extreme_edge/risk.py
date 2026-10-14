"""RSI extreme-edge risk: the author's rule — 1.5xATR(14) hard stop, target at
1.5x the stop distance (target_atr_mult = 1.5 * 1.5 = 2.25), max hold 72 bars
(3 days on 1h). No signal exits: every trade is managed by stop / target /
time. 1% risk per trade, 3x leverage cap."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.25,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# RSI(14) + ATR(14) settle comfortably inside 60 bars.
WARMUP = 60
