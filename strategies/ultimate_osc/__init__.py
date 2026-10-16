"""Larry Williams Ultimate Oscillator engine: registration + re-exports."""

from strategies.ultimate_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ultimate Oscillator divergence (Williams)",
        slug="ultimate_osc",
        description=(
            "Williams Ultimate Oscillator (7/14/28 buying-pressure "
            "averages); entries on regular price/UO divergence confirmed "
            "by fractal pivots; exits at UO 70/30 extremes; 2xATR stop, "
            "96-bar max hold."
        ),
        source_name="The Ultimate Oscillator — Larry Williams, S&C April 1985",
        source_url="https://en.wikipedia.org/wiki/Ultimate_oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
