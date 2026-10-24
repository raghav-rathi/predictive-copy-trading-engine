"""John Ehlers Roofing Filter: registration + re-exports."""

from strategies.ehlers_roofing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Roofing Filter",
        slug="ehlers_roofing",
        description=(
            "John Ehlers Roofing Filter (Cycle Analytics): a 48-bar "
            "high-pass filter followed by a 10-bar SuperSmoother. The "
            "roofing line itself is the signal — LONG when it crosses "
            "above zero, SHORT when it crosses below zero, exit on "
            "the opposite zero cross. 1.5xATR stop, 2xATR chandelier "
            "trail, 72-bar (~3-day) max hold."
        ),
        source_name="John Ehlers, Cycle Analytics for Traders — Roofing Filter",
        source_url="https://www.mesasoftware.com/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
