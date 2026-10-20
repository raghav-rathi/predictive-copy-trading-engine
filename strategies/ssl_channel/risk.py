"""SSL Channel risk config.

The channel flips do the trade management (exits on the opposite
flip), so there is no trailing and no fixed target. A hard 2xATR stop
covers false flips that immediately fail, and a 200-bar max hold
prevents a sideways regime from camping in a dead position.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # SMA(10) channel spin-up
