"""ARMS Index / TRIN risk config.

TRIN washout signals are short-lived mean-reversion setups: the
panic flush exhausts itself quickly, so the max hold is short
(24 bars, ~1 day) and the target is a modest 2xATR. The 1.5xATR
hard stop bounds the failure case — a washout that keeps washing
out. No trailing stop — exits are TRIN-driven (reversion into the
0.9-1.1 band), and the hard stop/target bound the failure case.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 20  # TRIN window (10 bars) + excursion lookback (10) + margin
