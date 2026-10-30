"""Aroon cross: registration + re-exports."""

from strategies.aroon_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Aroon Cross",
        slug="aroon_cross",
        description=(
            "Tushar Chande Aroon(25): Aroon Up crosses above "
            "Aroon Down while Aroon Up > 70 for longs, Aroon "
            "Down crosses above Aroon Up while Aroon Down > 70 "
            "for shorts, exit on the opposite cross. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Aroon, StockCharts ChartSchool (Tushar Chande, 1995)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:aroon",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
