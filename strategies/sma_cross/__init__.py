"""SMA(20)/SMA(50) crossover: registration + re-exports."""

from strategies.sma_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SMA Crossover",
        slug="sma_cross",
        description=(
            "Textbook moving-average crossover: long when SMA(20) crosses "
            "above SMA(50), short on the cross below, exit on the opposite "
            "cross. 2xATR stop, 2.5xATR chandelier trail, no fixed target, "
            "168-bar max hold."
        ),
        source_name="Moving-average crossover (Murphy, Technical Analysis of the Financial Markets)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
