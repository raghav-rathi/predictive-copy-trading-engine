"""CCI pivot divergence: registration + re-exports."""

from strategies.cci_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CCI Divergence",
        slug="cci_divergence",
        description=(
            "Donald Lambert CCI(20) pivot divergence: bullish when price "
            "makes a lower pivot low while CCI makes a higher pivot low "
            "within 40 bars, confirmed by a close above the prior 3-bar "
            "high; bearish mirror. Pivots lagged by 2 bars (no "
            "lookahead). Exit on the opposite divergence. 2xATR stop, "
            "2.5xATR trail, 168-bar max hold."
        ),
        source_name="CCI divergence (Donald Lambert; classic oscillator divergence, StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
