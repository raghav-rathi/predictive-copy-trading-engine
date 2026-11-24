"""Pi Cycle Top risk config.

A slow regime system: entries only happen on SMA(111) crossing
2xSMA(350), so a position is a multi-week regime bet, not a
pattern scalp. There is NO max-hold cap (max_hold_bars=None):
forcing an exit after 60 bars would cut a regime trade ~2.5 days
in, long before the opposite cross that defines the exit, and
would turn the system into a 60-bar timer rather than a Pi Cycle
trade. The exit is the opposite cross; the 2xATR hard stop and
3xATR chandelier trail are the only other ways out.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 400  # SMA(350) spin-up plus margin for the ratio to settle
