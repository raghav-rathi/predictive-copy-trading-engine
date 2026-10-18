"""ICT Silver Bullet engine: registration + re-exports."""

from strategies.ict_silver_bullet import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Silver Bullet Killzones (ICT)",
        slug="ict_silver_bullet",
        description=(
            "ICT Silver Bullet: NY killzones 03-04/10-11/14-15, 4h EMA(50) "
            "bias, entries on retrace into same-day unmitigated FVG with "
            "micro market-structure shift; 0.75xATR stop (FVG proxy), "
            "1.5xATR target (2R), 24-bar max hold."
        ),
        source_name="Michael Huddleston (ICT), 2022 mentorship",
        source_url="https://chartwhisperer.ca/blog/ict-silver-bullet-killzones-trading-guide",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
