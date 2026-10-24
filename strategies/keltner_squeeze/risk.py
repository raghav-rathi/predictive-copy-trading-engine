"""TTM-style squeeze breakout risk config.

Squeeze breakouts are expansion trades: once volatility releases,
the move can run, so the stop is a wider 2.0xATR (a breakout that
retraces less than 2 ATR is still a breakout) and the trail is
2.5xATR to give the expansion room, with no fixed target — the
opposite-band cross is the exit. The 96-bar (~4-day) max hold
fits the thesis: a genuine volatility expansion resolves within
days; a breakout that stalls for four days was a false release.
Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # BB(20) + KC EMA(20)/ATR(10) spin-up, with margin
