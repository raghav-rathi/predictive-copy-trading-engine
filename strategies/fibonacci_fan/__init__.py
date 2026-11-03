"""Fibonacci Fan: registration + re-exports."""

from strategies.fibonacci_fan import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Fan",
        slug="fibonacci_fan",
        description=(
            "Fibonacci fan (rolling 50-bar leg): fan lines radiate from the window low through the 38.2% and 61.8% retracement points of the low-to-high leg, extended forward at the leg's slope. Long on close cross above the 38.2% fan line, short on cross below the 61.8% fan line; exits on the opposite cross. Redrawn each bar from data through that bar only — no repainting of past signals."
        ),
        source_name="Fibonacci fan (classic charting)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:fibonacci_fan",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
