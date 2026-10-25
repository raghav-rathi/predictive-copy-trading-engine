"""Head and shoulders risk config.

Same reversal-pattern standard as double_top_bottom: 2xATR stop,
2.5xATR chandelier trail, no fixed target, 120-bar (5-day) max hold —
H&S formations take longer to resolve than double tops, so the hold
is a day longer. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # five zigzag pivots of spin-up, with margin
