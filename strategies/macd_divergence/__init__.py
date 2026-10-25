"""MACD histogram divergence: registration + re-exports."""

from strategies.macd_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Histogram Divergence",
        slug="macd_divergence",
        description=(
            "Aspray MACD-Histogram divergence on 5-bar zigzag pivots: long "
            "when price makes a lower low but the histogram makes a higher "
            "low, short on the mirror; exit when the histogram crosses back "
            "through zero after confirming, or on the opposite divergence. "
            "2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="MACD-Histogram divergence (Appel; Aspray, StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/~gitbook/pdf?page=5PiaPxqh63SVx6ShNFH8&only=yes&limit=100",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
