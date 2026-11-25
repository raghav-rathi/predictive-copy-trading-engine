"""EMA ribbon expansion risk config.

The ribbon exit (EMA8 crossing back through EMA13) is the
strategy's own exit, so the harness 2xATR hard stop / 3xATR
chandelier trail sit behind it as a safety net for gap-through
moves. No take-profit target — the trade rides the aligned
ribbon until alignment breaks. The 60-bar max hold keeps a
position from camping through a slow ribbon drift.
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

WARMUP = 60  # EMA55 spin-up (55 bars) plus compression window, with margin
