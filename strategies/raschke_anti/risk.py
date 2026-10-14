"""Raschke Anti risk.

The published method places the protective stop below the pullback
swing low. The backtest harness only supports static ATR stops, so a
2.0xATR hard stop approximates the pullback swing low (a typical
counter-move against the trend is ~1-2 ATR on hourly bars; 2.0x keeps
it outside the noise but inside the fade's tolerance). Exits are the
opposite setup plus a 3.0xATR chandelier trailing stop, per the
"exit on opposite setup or trailing stop" rule. 120-bar max hold.
"""

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

WARMUP = 90  # %D(10 of 7) + osc(3,10,16) need ~3x to stabilize
