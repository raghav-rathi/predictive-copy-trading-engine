"""Triple-EMA stack: registration + re-exports."""

from strategies.ema_triple_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA Triple Cross",
        slug="ema_triple_cross",
        description=(
            "Triple moving-average alignment (EMA 3/8/21): long only "
            "while stacked bullish (fast > mid > slow), short only "
            "while stacked bearish; exit on unstacking. 2xATR stop, "
            "3xATR trail, 336-bar max hold."
        ),
        source_name="Triple moving average system (classic trend system, StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-averages",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
