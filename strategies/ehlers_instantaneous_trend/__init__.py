"""Ehlers Instantaneous Trendline: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.ehlers_instantaneous_trend import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Instantaneous Trendline",
        slug="ehlers_instantaneous_trend",
        description=(
            "Ehlers Instantaneous Trendline (alpha = 0.07): LONG "
            "when price is above the trendline and the trendline is "
            "rising; SHORT when price is below it and it is falling. "
            "Entries are transition-only. Exit when price crosses "
            "back through the trendline or the trendline turns "
            "against the position."
        ),
        source_name="John Ehlers, Rocket Science for Traders (2001), Instantaneous Trendline chapter",
        source_url="https://www.mesasoftware.com/papers/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
