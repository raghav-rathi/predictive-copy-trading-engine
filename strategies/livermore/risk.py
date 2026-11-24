"""Livermore trend-system risk config.

The Livermore trade is a with-trend breakout: the entry
already requires rising swing lows (long) or falling swing
highs (short), so the exit is the structure failing — close
breaking the prior 10-bar low/high. There is no take-profit
target: Livermore's whole point is to ride a trend until it
proves itself over, and a fixed target would cut the runners
the system exists to catch. The 2xATR hard stop covers the
classic failure: the breakout was a false break and price
reverses straight back through the range. The 3xATR
chandelier trail protects the runners without a fixed target.
The 60-bar max hold keeps a position from camping through a
dead range where breakouts fire on noise and the 10-bar exit
never triggers.
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

WARMUP = 60  # 20-bar breakout window plus the 20-bar swing-low history, with margin
