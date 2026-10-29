"""Elder MACD-histogram reversal: registration + re-exports."""

from strategies.macd_histogram_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Histogram Reversal",
        slug="macd_histogram_reversal",
        description=(
            "Alexander Elder MACD-histogram slope flips: long on "
            "a histogram trough flip (first uptick after a "
            "decline) while the histogram is below zero, short on "
            "a peak flip while above zero. Exit on the opposite "
            "flip or a zero cross. 2xATR stop, 2xATR trail, "
            "72-bar max hold."
        ),
        source_name="MACD Histogram (Alexander Elder, Trading for a Living; StockCharts MACD ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-average-convergence-divergence-macd",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
