"""Turtle Soup engine: registration + re-exports."""

from strategies.turtle_soup import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Turtle Soup + Plus One (Raschke false-breakout fade)",
        slug="turtle_soup",
        description=(
            "Fade false 20-bar breakdowns: new 20-bar low with the prior low "
            ">=4 bars old, then close back above it within 3 bars; "
            "1.5xATR stop, 2xATR trail, 2.5xATR target, 24-bar max hold."
        ),
        source_name="Linda Raschke, Street Smarts (Turtle Soup)",
        source_url="https://roboforex.com/blog/education/trading-strategies-that-were-a-revolution-three-strategies-of-linda-raschke/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
