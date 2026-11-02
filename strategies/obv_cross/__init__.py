"""OBV Cross: registration + re-exports."""

from strategies.obv_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="OBV Cross",
        slug="obv_cross",
        description=(
            "On-Balance Volume vs its EMA(20): volume-flow confirmation — long when OBV crosses above its EMA, short below, exit on the opposite cross."
        ),
        source_name="On-Balance Volume (Joseph Granville)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:on_balance_volume",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
