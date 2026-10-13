"""jhadchiti trend risk: the author's sizing — 0.75% equity risk per trade
(risk_frac 0.0075), 3.0x max leverage. 2xATR(20) hard stop (the author's
stop), no trailing and no fixed target (the 20-period channel exit manages
winners); 2160-bar (90-day) max hold is the author's long-horizon cutoff
on 1h bars."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=20,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=2160,
    risk_frac=0.0075,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# BTC SMA(200) + 20-bar regime lookback dominates the warmup.
WARMUP = 230
