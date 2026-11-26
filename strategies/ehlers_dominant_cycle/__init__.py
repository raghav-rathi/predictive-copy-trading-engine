"""Ehlers dominant-cycle engine: registration + re-exports."""

from strategies.ehlers_dominant_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Dominant Cycle",
        slug="ehlers_dominant_cycle",
        description=(
            "John F. Ehlers' band-pass resonator (period 20, "
            "bandwidth 0.7) on a high-pass detrended close: long on "
            "the band-pass crossing above zero, short on it crossing "
            "below, exit on the opposite cross; dominant cycle "
            "period (2x bars between zero crossings, SMA-10, "
            "clamped 6-50) as a diagnostic; 2xATR stop, 3xATR trail, "
            "120-bar max hold."
        ),
        source_name="John F. Ehlers — Cycle Analytics for Traders (2013), band-pass filter chapter",
        source_url="https://docs.wickra.org/Indicators/Indicator-BandpassFilter",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
