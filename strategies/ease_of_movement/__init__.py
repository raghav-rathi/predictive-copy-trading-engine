"""Ease of Movement engine: registration + re-exports."""

from strategies.ease_of_movement import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ease of Movement zero-cross (Arms)",
        slug="ease_of_movement",
        description=(
            "EMV = midpoint-move / (volume/range), 14-bar SMA; entries on "
            "zero-line cross; exits on the opposite cross; 2xATR stop, "
            "96-bar max hold."
        ),
        source_name="Ease of Movement (EMV) — StockCharts ChartSchool",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
