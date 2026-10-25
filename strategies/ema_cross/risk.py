"""EMA crossover risk config.

The crossover itself is the whole trade idea, so risk is the house
standard: a roomy 2xATR stop (crossovers whipsaw; a tight stop just
pays fees faster), a 2.5xATR chandelier trail to ride a real trend,
no fixed target — the opposite cross is the exit — and a 7-day max
hold so a dead cross doesn't squat on capital. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=168,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # slow EMA (21) plus margin
