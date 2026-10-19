"""Williams A/D risk config -- momentum-confirmation system: hard 2xATR
stop, no trailing and no fixed target (the WAD-SMA cross-back exit
manages the trade), 60-bar max hold so stale accumulation signals do
not camp through chop, 1% risk per trade."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=60,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80
