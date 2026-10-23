"""Inside bar breakout risk config.

Inside-bar breakouts are short-horizon momentum trades: the edge
is the volatility expansion right out of the contraction, which is
why the setup expires after 5 bars. The stop is 1.5xATR (canon
places it on the opposite side of the mother bar; 1.5xATR is the
harness's parametrized stand-in), the target is 2R (the classic
inside-bar 2:1 minimum), no trailing stop (a trail would fight the
fixed 2R objective), and a 48-bar (~2 day) max hold -- a breakout
that hasn't expanded within two days is a failed breakout. Both
directions traded; 1% risk per trade, 3x leverage cap.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # ATR(14) spin-up + a few bars of setup history, with margin
