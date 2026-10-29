"""MACD Bollinger Bands: registration + re-exports."""

from strategies.macd_bollinger import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Bollinger",
        slug="macd_bollinger",
        description=(
            "Bollinger Bands (20, 2) applied to the MACD line "
            "(Carter-style): long when the MACD line crosses back "
            "up through its own lower band while below zero, short "
            "on the mirror cross down through the upper band while "
            "above zero. Exit on a cross back through the band "
            "midline or the MACD signal line. 2xATR stop, 2.5xATR "
            "trail, 168-bar max hold."
        ),
        source_name="Bollinger Bands on MACD (John Carter, Mastering the Trade; StockCharts MACD ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-average-convergence-divergence-macd",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
