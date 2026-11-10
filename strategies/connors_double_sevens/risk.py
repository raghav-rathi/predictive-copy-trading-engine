"""Connors Double 7s risk config.

The original system has NO stop loss and NO target — the exit is
purely the 7-day-high daily close. The harness risk layer is kept
effectively inert to stay faithful: a 10x ATR stop (a formality that
should essentially never fire), no trailing stop, no target, no max
hold. Sizing stays at the batch-standard 1% risk / 3x leverage cap
with Hyperliquid taker fees + slippage; with a 10x ATR stop the
risk-based notional is small (risk_frac / stop distance), which is
the honest consequence of an inert stop.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=10.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=False,
)

# 200 daily bars x 24 hourly bars: the SMA(200) of daily closes needs
# 200 days of history before the first eligible signal.
WARMUP = 4800
