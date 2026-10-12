"""Dual-Bear Pullback Short risk config -- the study's exit study: exits
matter most. Primary exit is the 4H EMA21 reclaim signal (in signals.py);
the harness adds a 2xATR(14) hard stop and a 240-bar (10-day) max-hold
backstop. No trailing, no fixed target — the reclaim exit does the trade
management. 1% risk/trade, 3x leverage cap. SHORT-ONLY: allow_longs is
False by design."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=240,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=False,
    allow_shorts=True,
)

WARMUP = 1500  # daily EMA55 (55d) + 4H EMA21 need ~62 days of 1h bars
