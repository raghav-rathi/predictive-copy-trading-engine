"""Time segmented volume: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.time_segmented_volume import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="Time Segmented Volume",
        slug="time_segmented_volume",
        description="Worden TSV(18): rolling 18-bar sum of (close - close[1]) * volume. Enter long when TSV crosses above zero, short when it crosses below zero; exit on the opposite cross.",
        source_name="Worden Brothers — Time Segmented Volume (TC2000 docs via Wickra)",
        source_url="https://docs.wickra.org/Indicators/Indicator-Tsv",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
