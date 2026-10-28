"""Cypher harmonic pattern: registration + re-exports."""

from strategies.cypher_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Cypher Harmonic Pattern",
        slug="cypher_pattern",
        description=(
            "Scott Carney Cypher on lagged 5-bar pivots within a "
            "60-bar window: AB retraces 38.2-61.8% of XA, BC "
            "extends 113-141.4% of AB, CD completes at 78.6% of XC "
            "(+/-8pp tolerance on each ratio). Bullish completion "
            "(X low, A high, B low, C high, D low) -> long; bearish "
            "mirror -> short. Exit on opposite pattern or 168-bar "
            "max hold. 2xATR stop, 2.5xATR trail."
        ),
        source_name="Scott Carney, Harmonic Trading — Cypher pattern",
        source_url="https://harmonictrading.com/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
