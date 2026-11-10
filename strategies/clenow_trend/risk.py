"""Clenow trend-following risk config.

Book-faithful exit: a 3x ATR trailing (chandelier) stop, which the
harness implements via trail_atr_mult on the entry-bar ATR. The hard
stop is set to the same 3x ATR distance. No take-profit target and no
max hold: Clenow lets winners run until the trailing stop (or the
opposite breakout) takes them out.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=720,          # 30-day ATR
    stop_atr_mult=3.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 2400  # 100-day slow EMA must be fully formed
