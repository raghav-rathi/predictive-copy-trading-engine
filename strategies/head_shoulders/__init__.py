"""Head and shoulders / inverse head and shoulders: registration + re-exports."""

from strategies.head_shoulders import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Head and Shoulders",
        slug="head_shoulders",
        description=(
            "Classic reversal on 5-bar zigzag pivots: head higher than two "
            "shoulders agreeing within 3%; trade the neckline break, exit "
            "on neckline reclaim or the opposite pattern. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Head and shoulders (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://securitiesmastery.com/stock-market-investing/technical-analysis/chart-patterns-and-trends/common-chart-patterns/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
