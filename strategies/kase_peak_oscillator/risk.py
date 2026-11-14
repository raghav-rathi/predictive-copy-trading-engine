"""Kase Peak Oscillator risk config.

KaseCD crosses are slow, regime-level turns (the PeakOscillator
averages ten KSDI horizons and the CD is its deviation from a
9-bar average), so positions need room: 150-bar (~6-day) max hold,
2xATR hard stop for the failed-turn case, 3xATR chandelier trail
to ride a leg once KCD confirms. No fixed target -- exits are
KCD-cross / PeakOut driven.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 310  # Spec said 260, corrected: PeakOsc needs 51 bars before the
# rolling-250 percentile window even starts, so PeakMax first forms at
# ~bar 299 (51 + 249). See CALIBRATION.md.
