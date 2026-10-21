"""Force Index risk config.

Pullback entries need room: a dip can keep dipping a bar or two before
turning, so the hard stop is a normal 2xATR (not the tighter
divergence-style stop). The 3xATR chandelier trail does the heavy lifting
once the trend resumes and runs. No fixed target — the exit rule (fi13
itself crossing zero, i.e. the balance of power flipping) is the exit.
max_hold_bars=100 lets a clean pullback-to-trend leg play out over
~4 days on 1h bars without camping through a regime change.
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

WARMUP = 60  # fi13 + ATR spin-up with margin
