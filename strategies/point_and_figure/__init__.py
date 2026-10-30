"""Point & Figure: registration + re-exports."""

from strategies.point_and_figure import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Point & Figure",
        slug="point_and_figure",
        description=(
            "Classic Point & Figure (Dorsey): 1%-of-price boxes, "
            "3-box reversal, X/O columns built causally from closes. "
            "Long on a double-top breakout (X column exceeds the "
            "previous X column high), short on a double-bottom "
            "breakdown, exit on a 3-box reversal (column flip). "
            "2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Point & Figure charts (StockCharts ChartSchool)",
        source_url="https://school.stockcharts.com/doku.php?id=chart_analysis:point_and_figure",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
