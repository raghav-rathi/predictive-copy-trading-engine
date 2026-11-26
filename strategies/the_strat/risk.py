"""The Strat risk config.

House standard: 2xATR hard stop, 3xATR chandelier trail, no
take-profit target, 120-bar max hold, 1% risk/trade, 3x
leverage cap. The signal exit (opposite Strat setup) is the
primary exit; the harness stops sit behind it for gap-through
moves and for reversals that never print a clean setup.
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

WARMUP = 200  # weekly FTFC needs 168 bars + margin
