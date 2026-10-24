"""Order-block retest risk config.

Retest entries buy/sell into a level that already proved itself
once (the displacement origin), so the stop is a roomy 2xATR with
a 2xATR chandelier trail, and no fixed target — the block-violation
and opposite-displacement signal exits do the trade management.
The 96-bar (~4-day) max hold fits the retest thesis: a block that
hasn't resolved in four days is stale, not a retest. Long/short
symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # ATR(14) + displacement + block scan spin-up, with margin
