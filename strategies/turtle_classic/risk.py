"""Original Turtle Rules risk config.

2xATR(20) hard stop = the Turtles' 2N stop (the "N" is ATR(20)). No
chandelier trail: Turtle exits are channel-based (10-bar for System 1,
20-bar for System 2), so trail_atr_mult is None by design. No fixed
target either -- the Turtles rode trends until the exit channel broke.

Pyramiding is deliberately omitted: the original added a unit every
0.5N up to 4 units, but this build trades a single unit per position
(1% equity risk on the 2N stop, 3x leverage cap). max_hold_bars=500 is
a backtest guardrail against a position that never touches its exit
channel, not part of the original rules.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=20,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=500,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 120  # 55-bar failsafe channel + ATR(20) spin-up, with margin
