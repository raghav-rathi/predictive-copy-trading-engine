"""Ulcer Index regime-gate risk config.

UI-gated Donchian breakouts are medium-horizon trend trades: the
entry already demands a calm regime, so the stop can be tight-ish
(1.5xATR) — a breakout that immediately reverses into stress is
exactly what the UI gate is supposed to filter, and the 2xATR
chandelier trail takes over once the leg extends. No fixed target:
exits are regime/signal-driven. 120-bar (~5 day) max hold keeps a
stalled breakout from tying up capital. Long-only (allow_shorts=False)
because the UI is a downside-risk gauge, not an upside-exhaustion one.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 60  # UI(14) + Donchian(20) spin-up, with margin
