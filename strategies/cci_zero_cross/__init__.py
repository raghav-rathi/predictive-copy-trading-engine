"""CCI zero-line trend-cross: registration + re-exports."""

from strategies.cci_zero_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CCI Zero Cross",
        slug="cci_zero_cross",
        description=(
            "Donald Lambert CCI(20) zero-line crosses with a "
            "trend filter: long on a cross above zero while price "
            "is above SMA(50), short on a cross below zero while "
            "price is below SMA(50). Crosses against the trend are "
            "ignored. Exit on the opposite zero cross. 2xATR stop, "
            "3xATR trail, 240-bar max hold."
        ),
        source_name="CCI zero-line trend (Donald Lambert; StockCharts ChartSchool CCI)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
