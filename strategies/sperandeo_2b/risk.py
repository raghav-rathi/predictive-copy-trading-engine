"""Sperandeo 2B false-breakout reversal risk config (batch-standard risk layer).

Stop: 2.0x ATR (the harness ATR stop approximates Sperandeo's stop
above the false-breakout high / below the false-breakout low; see
CALIBRATION.md). Target: 10.0x ATR, i.e. 5x the 2.0x ATR stop
distance, matching Sperandeo's suggestion of up to 5x the stop.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=10.0,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40
