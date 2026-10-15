"""Chaikin Oscillator engine: registration + re-exports."""

from strategies.chaikin_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin Oscillator zero-cross (Chaikin)",
        slug="chaikin_osc",
        description=(
            "CHO = EMA3(ADL) - EMA10(ADL); entries on zero-line cross; "
            "exits on the opposite cross; 1.5xATR stop, 72-bar max hold."
        ),
        source_name="Chaikin Oscillator — StockCharts ChartSchool",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
