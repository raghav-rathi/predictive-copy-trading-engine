"""Ehlers Instantaneous Trendline engine: registration + re-exports."""

from strategies.ehlers_instantaneous import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Instantaneous Trendline",
        slug="ehlers_instantaneous",
        description=(
            "John Ehlers Instantaneous Trendline (alpha=0.07, Cycle "
            "Analytics for Traders): LONG when close crosses above the "
            "trendline, SHORT when it crosses below. Exit on the "
            "opposite cross. 1.5xATR stop, 2xATR chandelier trail, "
            "72-bar max hold."
        ),
        source_name="Instantaneous Trendline (John Ehlers)",
        source_url="https://www.fmz.com/lang/en/strategy/436000",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
