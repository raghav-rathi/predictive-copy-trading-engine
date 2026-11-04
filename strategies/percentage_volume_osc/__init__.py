"""Percentage Volume Oscillator: registration + re-exports."""

from strategies.percentage_volume_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Percentage Volume Oscillator",
        slug="percentage_volume_osc",
        description="PVO (12, 26, 9): the MACD of volume — 100*(EMA12(v)-EMA26(v))/EMA26(v) with a 9-period signal line. Long on a PVO cross above its signal line while price holds above SMA(50); short on a cross below while price holds below SMA(50); exit on the opposite cross.",
        source_name="Percentage Volume Oscillator (StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/~gitbook/pdf?page=AujMj8CJKpAa7EHWRU4k&only=yes&limit=100",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
