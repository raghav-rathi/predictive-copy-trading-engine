"""Chaikin ADL trend engine: registration + re-exports."""

from strategies.chaikin_adl_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin ADL Trend",
        slug="chaikin_adl_trend",
        description=(
            "Marc Chaikin Accumulation/Distribution Line cross: LONG "
            "when the ADL crosses above its SMA(10) while close is above "
            "SMA(50), SHORT on the mirror. Exit on the opposite ADL "
            "cross. 1.5xATR stop, 2xATR chandelier trail, 72-bar max hold."
        ),
        source_name="Accumulation/Distribution Line (Marc Chaikin)",
        source_url="https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:accumulation_distribution_line",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
