"""DMI cross: registration + re-exports."""

from strategies.dmi_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DMI Cross",
        slug="dmi_cross",
        description=(
            "Wilder Directional Movement: +DI crosses above -DI "
            "while ADX(14) > 20 for longs, -DI crosses above +DI "
            "while ADX(14) > 20 for shorts, exit on the opposite "
            "DI cross. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Average Directional Index (ADX), StockCharts ChartSchool (Wilder, New Concepts in Technical Trading Systems, 1978)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
