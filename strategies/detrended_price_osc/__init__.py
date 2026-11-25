"""Detrended Price Oscillator engine: registration + re-exports."""

from strategies.detrended_price_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Detrended Price Oscillator",
        slug="detrended_price_osc",
        description=(
            "StockCharts ChartSchool Detrended Price Oscillator: "
            "DPO(20) = close minus SMA(close, 20) shifted back 11 "
            "bars (20/2 + 1); long when DPO crosses above 0, short "
            "when it crosses below 0, exit on the opposite cross; "
            "2xATR stop, 3xATR trail, 60-bar max hold."
        ),
        source_name="StockCharts ChartSchool, Detrended Price Oscillator (DPO)",
        source_url="https://chartschool.stockcharts.com/~gitbook/pdf?page=prVTFcIEDZPUBw709AIs&only=yes&limit=100",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
