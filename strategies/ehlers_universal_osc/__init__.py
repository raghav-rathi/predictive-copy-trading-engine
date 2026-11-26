"""Ehlers universal oscillator engine: registration + re-exports."""

from strategies.ehlers_universal_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Universal Oscillator",
        slug="ehlers_universal_osc",
        description=(
            "John F. Ehlers' adaptive band-pass oscillator: two-pole "
            "resonator (period 20, bandwidth 0.3) on median price, "
            "AGC-normalized by its rolling 100-bar RMS, trigger line "
            "0.9x the prior bar's normalized output; long on the "
            "normalized output crossing above the trigger, short on "
            "it crossing below, exit on the opposite cross; 2xATR "
            "stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="John F. Ehlers — Cycle Analytics for Traders (2013), band-pass filter chapter",
        source_url="https://www.tradingview.com/script/jtvNFAgS-Ehlers-Band-Pass-Filter/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
