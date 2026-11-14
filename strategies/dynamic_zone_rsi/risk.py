"""Dynamic Zones RSI risk config.

Mean-reversion bounce entries need room for RSI to travel from the
zone back toward 50, so the max hold is 120 bars (~5 days) and the
3xATR chandelier trail does the lifting once a bounce extends. The
2xATR hard stop handles the failure case -- an oversold bounce that
rolls back over is usually a quick reversal, so a tight stop keeps
those losers small. No fixed target -- exits are RSI-driven.
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
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # 70-bar percentile zones + RSI(14) spin-up, with margin
