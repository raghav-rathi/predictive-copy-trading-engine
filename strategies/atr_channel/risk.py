"""ATR channel breakout risk config.

Breakouts that fail do so fast, so the trail is wider than the stop
here (3xATR trail vs 2xATR stop): give a real breakout room to run,
but let the midline signal exit do most of the failing-trade work.
120-bar (5-day) max hold. Long/short symmetric.
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
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # SMA(20) plus margin
