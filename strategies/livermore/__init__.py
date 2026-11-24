"""Livermore engine: registration + re-exports."""

from strategies.livermore import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Livermore",
        slug="livermore",
        description=(
            "Jesse Livermore trend system: long on a close above "
            "the prior 20-bar high with higher swing lows (10-bar "
            "low ending 10 bars ago above the one ending 20 bars "
            "ago); short mirror with lower highs; exit on a break "
            "of the prior 10-bar low/high; 2xATR stop, 3xATR trail, "
            "60-bar max hold."
        ),
        source_name='Jesse Livermore, "How to Trade in Stocks" (1940)',
        source_url="https://www.mql5.com/en/articles/24075",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
