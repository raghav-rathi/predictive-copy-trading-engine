"""Balance of Power risk config.

BOP regime legs can persist (buyers stay in control for a stretch),
so the max hold is generous (150 bars, ~6 days) and a 2.5xATR
chandelier trail holds winners through the chop around the zero
line. The 2xATR hard stop handles the failure case — a fresh control
shift that immediately reverses. No fixed target — BOP exits are
zero-cross-driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 30  # SMA(14) spin-up (14 bars) plus margin for stable reads
