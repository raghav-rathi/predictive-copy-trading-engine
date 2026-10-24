"""Elder SafeZone risk config.

The SafeZone line itself is the exit, so the ATR stop/trail are
catastrophe backstops, not the primary exit: a 2.0xATR hard stop
and a 2.5xATR chandelier trail sit behind the line. The 96-bar
(~4-day) max hold fits the trend-following thesis: a SafeZone
trend trade that hasn't resolved in four days is chop, not trend.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # EMA(22) + SafeZone(10) spin-up, with margin
