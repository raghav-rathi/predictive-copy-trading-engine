"""Wyckoff accumulation risk config.

House standard except the direction: 2xATR hard stop, 3xATR
chandelier trail, no take-profit target, 240-bar max hold
(an accumulation schematic plays out over days to weeks on
1h bars), 1% risk/trade, 3x leverage cap. LONG ONLY:
allow_shorts=False -- accumulation is a bullish schematic;
the mirror distribution setup is a different strategy.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 200  # range window (120) + ATR/vol warmup + margin
