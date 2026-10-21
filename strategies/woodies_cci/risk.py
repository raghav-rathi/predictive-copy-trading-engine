"""Woodies CCI risk config.

The Zero-Line Reject is a with-trend pullback entry: the setup
itself (6 bars on one side of the zero line) already filters for
trend, so there is no take-profit target — the exit is the trend
line losing its side of the zero line, i.e. the premise expiring.
The 2xATR hard stop covers the pattern's classic failure: the turbo
hooks up, the pullback deepens past the zero line anyway, and the
"reject" becomes a reversal. The 3xATR chandelier trail protects
the runners without a fixed target. The 60-bar max hold keeps a
position from camping through a sideways zero-line chop where
turbo hooks fire repeatedly on no trend.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # CCI(14) mean-deviation spin-up plus the 6-bar trend-run qualifier, with margin
