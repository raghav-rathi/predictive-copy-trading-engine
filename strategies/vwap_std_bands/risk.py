"""VWAP std bands risk config.

Mean-reversion to the session VWAP gets the house-standard
leash: 2xATR stop, 2.5xATR trail, no fixed target (the VWAP
midline manages the trade), 120-bar (5-day) max hold — the
hold is a backstop only, since a session-VWAP trade should
resolve within its day. Long/short symmetric.
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

# 20-bar sigma window plus ATR(14), plus margin.
WARMUP = 25
