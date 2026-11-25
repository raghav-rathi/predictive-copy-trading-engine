"""ADX Bollinger squeeze risk config.

The signal exit (close back inside the bands, or ADX falling
below 15) is the primary exit, so the harness 2xATR hard stop /
3xATR chandelier trail sit behind it as a safety net for
gap-through-band moves (the breakout is only recognised at the
close). No take-profit target — the trade rides the expansion
until the close comes back inside the bands or momentum fades.
The 60-bar max hold keeps a position from camping through a
slow post-squeeze drift.
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

WARMUP = 50  # BB(20) + squeeze 20-bar min + ADX(14) spin-up, with margin
