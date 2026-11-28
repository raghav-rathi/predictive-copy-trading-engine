"""Wyckoff distribution risk config.

House standard except the direction and hold: 2xATR hard
stop, 3xATR chandelier trail, no take-profit target, 120-bar
max hold (a distribution schematic plays out over days on
1h bars), 1% risk/trade, 3x leverage cap. SHORT ONLY:
allow_longs=False -- distribution is a bearish schematic;
the mirror accumulation setup is a different strategy.
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
    allow_longs=False,
    allow_shorts=True,
)

WARMUP = 150  # range window (120) + ATR/vol warmup + margin
