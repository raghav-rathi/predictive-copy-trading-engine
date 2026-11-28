"""Popgun engine: registration + re-exports."""

from strategies.popgun import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Popgun Bar Pattern (Jeffrey Kennedy)",
        slug="popgun",
        description=(
            "Jeffrey Kennedy Popgun: an inside bar followed "
            "by an outside bar that engulfs it arms a "
            "high/low bracket; a close crossing above the "
            "outside bar's high (long) or below its low "
            "(short) within the next 5 bars enters. Exit "
            "on a close back through the arming level or "
            "the opposite entry; 2xATR stop, 3xATR trail, "
            "48-bar max hold."
        ),
        source_name="Popgun bar pattern — Jeffrey Kennedy / Elliott Wave International",
        source_url="https://elliottwaveuniversity.com/popgun-twobar-pattern-points-trade-setups/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
