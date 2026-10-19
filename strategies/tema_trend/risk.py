"""TEMA trend risk config -- dual-TEMA trend system: wider 2.5xATR hard
stop (TEMA whipsaws on 1h crypto), 3xATR chandelier trailing to let
trends run, no fixed target (the TEMA cross-back exits manage the
trade), 120-bar max hold."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.5,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 260
