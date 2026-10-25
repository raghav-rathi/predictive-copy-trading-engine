"""Double top / double bottom: registration + re-exports."""

from strategies.double_top_bottom import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Double Top / Double Bottom",
        slug="double_top_bottom",
        description=(
            "Classic reversal: two swing highs within 1.5% (double top) or "
            "two swing lows within 1.5% (double bottom) on 5-bar zigzag "
            "pivots; trade the neckline break, exit on neckline reclaim or "
            "the opposite pattern. 2xATR stop, 2.5xATR trail, 96-bar max hold."
        ),
        source_name="Double top / double bottom (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://securitiesmastery.com/stock-market-investing/technical-analysis/chart-patterns-and-trends/common-chart-patterns/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
