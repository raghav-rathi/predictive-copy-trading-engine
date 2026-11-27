"""Wyckoff accumulation engine: registration + re-exports."""

from strategies.wyckoff_accumulation import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wyckoff Accumulation",
        slug="wyckoff_accumulation",
        description=(
            "Wyckoff accumulation schematic, LONG ONLY: after "
            "a >=5% decline over 120 bars, a spring (false "
            "breakdown below the 120-bar low, close reclaimed "
            "within 3 bars) enters long; a sign of strength "
            "(wide up bar closing above the range midpoint) "
            "followed by a last point of support (higher-low "
            "pullback holding above the spring low) enters "
            "long again. Exit below spring_low or above the "
            "range projection; 2xATR stop, 3xATR trail, "
            "240-bar max hold."
        ),
        source_name="Wyckoff accumulation — ChartGuys",
        source_url="https://www.chartguys.com/chart-patterns/wyckoff-accumulation",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
