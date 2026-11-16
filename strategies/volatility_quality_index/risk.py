"""VQI risk config.

VQI is a regime-quality read, not a level: it says volatility is
currently directional, not where price is going. Entries therefore
get a 1.5xATR stop and a 2R target (2.0xATR) -- the trade is a bet
that the directional-volatility regime persists long enough to pay
2R -- and a short 48-bar max hold (~2 days), because a VQI regime
that has not paid within two days is stale. No trail: the VQI-change
flip and the EMA20 cross are the exits.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # 10-bar S + 14-bar WMA + 10-bar change + 50-bar gate median
