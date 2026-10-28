"""MACD zero-line cross: registration + re-exports."""

from strategies.macd_zero_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Zero Cross",
        slug="macd_zero_cross",
        description="MACD(12,26,9) line crosses above zero = long, below zero = short; exit on the opposite zero cross. 2xATR stop, 2.5xATR trail, 168-bar max hold.",
        source_name="MACD (Gerald Appel; StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-average-convergence-divergence-macd",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
