"""Minervini Trend Template risk config.

Minervini's rule is a 7-8% stop below entry. RiskConfig only
offers an ATR-multiple stop, so the multiple is chosen so the
typical stop lands near 7.5% of price: 1h ATR(14) on BTC/ETH runs
roughly 0.8-1.5% of price, so 6xATR is ~5-9%, centred near the
7.5% target. This is an approximation, documented here and in
CALIBRATION.md — the stop is NOT a fixed 7.5% of entry price; it
widens in volatile regimes and tightens in quiet ones, which is
the faithful ATR translation of the rule.

The 8xATR chandelier trail rides the SEPA trend once it runs;
no fixed target (Minervini lets winners run). The 720-bar
(~30-day) max hold fits the weeks-to-months trend-ride thesis:
a base breakout that has not run in a month was not a SEPA move.
Long/short symmetric (short mirror is builder-added).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=6.0,
    trail_atr_mult=8.0,
    target_atr_mult=None,
    max_hold_bars=720,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# SMA(200) + 720-bar slope lookback, with margin.
WARMUP = 960
