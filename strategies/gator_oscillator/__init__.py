"""Gator Oscillator states engine: registration + re-exports."""

from strategies.gator_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gator Oscillator States",
        slug="gator_oscillator",
        description=(
            "Gator Oscillator (Bill Williams): abs(jaw-teeth) above zero, "
            "-abs(teeth-lips) below zero from SMMA balance lines (13/8/5 "
            "on median price, displaced 8/5/3); bars green when |value| "
            "rises. Long on the awakes->eats flip with lips>teeth>jaw "
            "fan, short with lips<teeth<jaw fan; exits when the Gator "
            "sleeps (both red) or the fan order flips; 2xATR stop, 3xATR "
            "chandelier trail, 150-bar max hold."
        ),
        source_name="Gator Oscillator (Bill Williams)",
        source_url="https://www.ifcmfa.com/en/ntx-indicators/gator-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
