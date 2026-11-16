"""FFT dominant-cycle risk config.

The reconstructed cycle is a smoothed, lagging view of the last 128
bars: entries arrive after the turn has started, so the 1.5xATR stop
absorbs the whipsaw when the cycle flips back, and the 2.5xATR target
banks the leg when the cycle actually extends. Max hold 96 bars
(~4 days) caps exposure to a cycle that has stopped turning -- the
FFT assumes stationary cycles and crypto cycles drift, so a stale
cycle signal should not be carried indefinitely. No trail: the
slope-flip exit is the trailing mechanism.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.5,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 180  # 128-bar FFT window + SMA(50) spin-up + margin
