"""Bull / bear flag breakout: registration + re-exports."""

from strategies.flag_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Flag Pattern Breakout",
        slug="flag_pattern",
        description=(
            "Textbook flag: a >=3xATR pole within 12 bars, then a 5-15 bar "
            "consolidation spanning <=1.5xATR and retracing <=60% of the "
            "pole; trade the breakout in the pole's direction, exit on a "
            "close back through the level or the opposite flag. 1.5xATR "
            "stop, 2xATR trail, 72-bar max hold."
        ),
        source_name="Flag pattern (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://securitiesmastery.com/stock-market-investing/technical-analysis/chart-patterns-and-trends/common-chart-patterns/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
