"""McGinley Dynamic engine: registration + re-exports."""

from strategies.mcginley_dynamic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="McGinley Dynamic cross (McGinley)",
        slug="mcginley_dynamic",
        description=(
            "Speed-adaptive MD(10)/MD(30) cross; entries on the cross; "
            "exits on the opposite cross; 2xATR stop, 96-bar max hold."
        ),
        source_name="McGinley Dynamic — TradingPedia",
        source_url="https://www.tradingpedia.com/forex-trading-indicators/mcginley-dynamic/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
