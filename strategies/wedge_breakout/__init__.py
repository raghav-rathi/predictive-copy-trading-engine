"""Rising / falling wedge breakout: registration + re-exports."""

from strategies.wedge_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wedge Breakout",
        slug="wedge_breakout",
        description=(
            "Converging trendlines through the last two swing highs and "
            "lows: rising wedge (highs rising slower than lows) traded "
            "short on a close below the lower line; falling wedge traded "
            "long on a close above the upper line; exit on a close back "
            "inside or the opposite breakout. 2xATR stop, 2.5xATR trail, "
            "96-bar max hold."
        ),
        source_name="Rising / falling wedges (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://learn.stocktrak.com/category/advanced/technical-analysis/charts-patterns/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
