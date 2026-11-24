"""UT Bot Alerts risk config.

The trailing stop IS the strategy's exit logic, so the harness
2xATR hard stop / 3xATR chandelier trail sit behind it as a
safety net for gap-through-stop moves (the stop flip itself is
only recognised at the close, so an adverse gap can run past
it). No take-profit target — the trade rides the trailing stop
until it flips. The 60-bar max hold keeps a position from
camping through sideways stop-flip chop.
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

WARMUP = 30  # ATR(10) spin-up plus stop-recursion settling, with margin
