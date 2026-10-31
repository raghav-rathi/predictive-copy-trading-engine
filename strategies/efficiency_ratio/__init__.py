"""Efficiency Ratio: registration + re-exports."""

from strategies.efficiency_ratio import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Efficiency Ratio",
        slug="efficiency_ratio",
        description=(
            "Kaufman Efficiency Ratio trend filter gating an EMA cross: "
            "long on EMA(9) crossing above EMA(21) while ER(10) > 0.3, "
            "short on the mirror cross while ER(10) > 0.3; exits on the "
            "opposite EMA cross with no ER condition. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Kaufman's Adaptive Moving Average (StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/~gitbook/pdf?page=VEzdy31Qvi7cxEUjmhji&only=yes&limit=100",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
