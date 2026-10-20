"""Waddah Attar Explosion risk config.

The explosion/dead-zone filters are the entry gate; the histogram
crossing back under the explosion line is the trade manager, so there
is no fixed target. A hard 2xATR stop plus a 3xATR chandelier trail
handle momentum failure (WAE longs fail fast when the explosion line
rolls over). A 200-bar max hold caps exposure in slow grinds.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 130  # ATR(100) dead zone + explosion(20) + EMA(40) spin-up
