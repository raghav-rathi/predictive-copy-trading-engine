"""Elder Impulse System engine: registration + re-exports."""

from strategies.elder_impulse import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Impulse System",
        slug="elder_impulse",
        description=(
            "Elder's impulse color: green when EMA13 and MACD histogram both "
            "rise, red when both fall, blue otherwise; long on green, short "
            "on red, flat on flip; 1.5xATR stop, 48-bar max hold."
        ),
        source_name="Alexander Elder — Elder Impulse System (Come Into My Trading Room)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-types/elder-impulse-system.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
