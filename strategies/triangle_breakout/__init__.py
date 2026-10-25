"""Ascending / descending triangle breakout: registration + re-exports."""

from strategies.triangle_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Triangle Breakout",
        slug="triangle_breakout",
        description=(
            "Ascending triangle (flat resistance within 1%, rising support) "
            "traded long on a close above resistance; descending triangle "
            "traded short on a close below support; exit on a close back "
            "inside or the opposite breakout. 2xATR stop, 2.5xATR trail, "
            "96-bar max hold."
        ),
        source_name="Ascending / descending triangles (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://securitiesmastery.com/stock-market-investing/technical-analysis/chart-patterns-and-trends/common-chart-patterns/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
