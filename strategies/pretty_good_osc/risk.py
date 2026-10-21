"""Pretty Good Oscillator risk config.

The PGO structure does its own trade management: entries fire on a
+3 ATR breakout thrust and exits print when the close decays back
through its 14-bar SMA (PGO crosses zero) — so there is no fixed
target and no trailing: trailing would fight the mean-reversion exit,
which is the whole point of the system (breakout, then take it off at
the mean). The 2xATR hard stop covers gap/reversal shock; the 100-bar
max hold is a backstop for a breakout that keeps running without ever
touching its SMA. Shorts are allowed: a -3 ATR thrust is symmetric to
the long case, and Johnson's breakout framing makes no directional
claim.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=100,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # SMA(14) of ATR(14) spin-up, with margin
