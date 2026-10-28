"""Triple top/bottom reversal: registration + re-exports."""

from strategies.triple_top_bottom import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Triple Top / Bottom",
        slug="triple_top_bottom",
        description=(
            "Classic triple top/bottom reversal on 2-bar-lagged pivots: "
            "three pivot highs within 1.5% of each other, separated by at "
            "least 5 bars inside a 60-bar window, confirmed by a close "
            "below the lowest intervening pivot low (short); the mirror "
            "for triple bottoms (long). Exit on the opposite pattern. "
            "2xATR stop, 2.5xATR trail, 168-bar max hold."
        ),
        source_name="Triple top/bottom reversal (Edwards & Magee; StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-patterns/triple-top-reversal",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
